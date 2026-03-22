#include "cnxt/runtime/ownership.h"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;

std::atomic<std::uint64_t> DestructionCount{0};
volatile std::uint64_t Sink = 0;

struct Options {
  std::uint64_t Iterations = 200000;
  std::uint64_t WarmupIterations = 20000;
  bool Json = false;
};

struct Result {
  std::string Name;
  double NsPerIteration = 0.0;
  std::string Baseline;
  double RatioToBaseline = 0.0;
};

struct Payload {
  std::uint64_t Value = 0;

  explicit Payload(std::uint64_t InitialValue) : Value(InitialValue) {}

  ~Payload() { DestructionCount.fetch_add(1, std::memory_order_relaxed); }
};

void destroyPayload(void *Object) { static_cast<Payload *>(Object)->~Payload(); }

void consume(std::uint64_t Value) {
  Sink += Value;
  std::atomic_signal_fence(std::memory_order_seq_cst);
}

[[noreturn]] void usageError(const char *Program, const char *Message) {
  std::cerr << Message << "\n"
            << "usage: " << Program
            << " [--iterations N] [--warmup N] [--json]\n";
  std::exit(1);
}

std::uint64_t parseUnsigned(const char *Program, const char *Flag,
                            const char *ValueText) {
  char *End = nullptr;
  unsigned long long Parsed = std::strtoull(ValueText, &End, 10);
  if (!ValueText[0] || !End || *End != '\0' || Parsed == 0)
    usageError(Program, Flag);
  return static_cast<std::uint64_t>(Parsed);
}

Options parseOptions(int argc, char **argv) {
  Options Opts;
  for (int I = 1; I < argc; ++I) {
    if (std::strcmp(argv[I], "--iterations") == 0) {
      if (I + 1 >= argc)
        usageError(argv[0], "--iterations requires a numeric argument");
      Opts.Iterations =
          parseUnsigned(argv[0], "invalid --iterations value", argv[++I]);
      continue;
    }
    if (std::strcmp(argv[I], "--warmup") == 0) {
      if (I + 1 >= argc)
        usageError(argv[0], "--warmup requires a numeric argument");
      Opts.WarmupIterations =
          parseUnsigned(argv[0], "invalid --warmup value", argv[++I]);
      continue;
    }
    if (std::strcmp(argv[I], "--json") == 0) {
      Opts.Json = true;
      continue;
    }
    if (std::strcmp(argv[I], "--help") == 0) {
      std::cout << "usage: " << argv[0]
                << " [--iterations N] [--warmup N] [--json]\n";
      std::exit(0);
    }
    usageError(argv[0], "unknown option");
  }
  return Opts;
}

template <typename Fn> double measure(const Options &Opts, Fn &&Body) {
  for (std::uint64_t I = 0; I < Opts.WarmupIterations; ++I)
    Body();

  auto Start = Clock::now();
  for (std::uint64_t I = 0; I < Opts.Iterations; ++I)
    Body();
  auto End = Clock::now();

  std::chrono::duration<double, std::nano> Elapsed = End - Start;
  return Elapsed.count() / static_cast<double>(Opts.Iterations);
}

Result benchmarkStdUniqueDrop(const Options &Opts) {
  return {"std_unique_drop",
          measure(Opts, [] {
            auto Owner = std::make_unique<Payload>(7);
            consume(Owner->Value);
          })};
}

Result benchmarkRuntimeUniqueDrop(const Options &Opts) {
  return {"runtime_unique_drop",
          measure(Opts, [] {
            void *Object =
                __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
            new (Object) Payload(7);
            consume(static_cast<Payload *>(Object)->Value);
            __cnxt_rt_own_v1_unique_drop(Object, destroyPayload, sizeof(Payload),
                                         alignof(Payload));
          }),
          "std_unique_drop"};
}

Result benchmarkStdSharedCopy(const Options &Opts) {
  auto Owner = std::make_shared<Payload>(11);
  return {"std_shared_copy",
          measure(Opts, [&] {
            std::shared_ptr<Payload> Alias = Owner;
            consume(Alias->Value);
          })};
}

Result benchmarkRuntimeSharedCopy(const Options &Opts) {
  void *Object = __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
  new (Object) Payload(11);
  void *Control = __cnxt_rt_own_v1_shared_from_unique(
      Object, destroyPayload, sizeof(Payload), alignof(Payload));

  Result R{"runtime_shared_copy_release",
           measure(Opts, [&] {
             __cnxt_rt_own_v1_shared_retain(Control);
             auto *Alias =
                 static_cast<Payload *>(__cnxt_rt_own_v1_shared_get(Control));
             consume(Alias ? Alias->Value : 0);
             __cnxt_rt_own_v1_shared_release(Control);
           }),
           "std_shared_copy"};

  __cnxt_rt_own_v1_shared_release(Control);
  return R;
}

Result benchmarkStdWeakLockHit(const Options &Opts) {
  auto Owner = std::make_shared<Payload>(13);
  std::weak_ptr<Payload> Observer = Owner;
  return {"std_weak_lock_hit",
          measure(Opts, [&] {
            std::shared_ptr<Payload> Locked = Observer.lock();
            consume(Locked ? Locked->Value : 0);
          })};
}

Result benchmarkRuntimeWeakLockHit(const Options &Opts) {
  void *Object = __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
  new (Object) Payload(13);
  void *Control = __cnxt_rt_own_v1_shared_from_unique(
      Object, destroyPayload, sizeof(Payload), alignof(Payload));
  __cnxt_rt_own_v1_weak_retain(Control);

  Result R{"runtime_weak_lock_hit",
           measure(Opts, [&] {
             void *Locked = __cnxt_rt_own_v1_weak_lock(Control);
             auto *Value =
                 static_cast<Payload *>(__cnxt_rt_own_v1_shared_get(Locked));
             consume(Value ? Value->Value : 0);
             __cnxt_rt_own_v1_shared_release(Locked);
           }),
           "std_weak_lock_hit"};

  __cnxt_rt_own_v1_shared_release(Control);
  __cnxt_rt_own_v1_weak_release(Control);
  return R;
}

Result benchmarkStdWeakLockMiss(const Options &Opts) {
  auto Owner = std::make_shared<Payload>(17);
  std::weak_ptr<Payload> Observer = Owner;
  Owner.reset();
  return {"std_weak_lock_miss",
          measure(Opts, [&] {
            std::shared_ptr<Payload> Locked = Observer.lock();
            consume(Locked ? 1 : 0);
            consume(Observer.expired() ? 1 : 0);
          })};
}

Result benchmarkRuntimeWeakLockMiss(const Options &Opts) {
  void *Object = __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
  new (Object) Payload(17);
  void *Control = __cnxt_rt_own_v1_shared_from_unique(
      Object, destroyPayload, sizeof(Payload), alignof(Payload));
  __cnxt_rt_own_v1_weak_retain(Control);
  __cnxt_rt_own_v1_shared_release(Control);

  Result R{"runtime_weak_lock_miss",
           measure(Opts, [&] {
             void *Locked = __cnxt_rt_own_v1_weak_lock(Control);
             consume(Locked ? 1 : 0);
             consume(__cnxt_rt_own_v1_weak_expired(Control));
             if (Locked)
               __cnxt_rt_own_v1_shared_release(Locked);
           }),
           "std_weak_lock_miss"};

  __cnxt_rt_own_v1_weak_release(Control);
  return R;
}

struct Counter {
  std::uint64_t Value = 0;

  int next() { return static_cast<int>(++Value); }
};

struct CounterLikeTag {};

template <typename T> struct CNxtIfaceWitness {
  const void *Table = nullptr;
};

template <typename T> struct CNxtIfaceBorrowed {
  void *Object = nullptr;
  const CNxtIfaceWitness<T> *Witness = nullptr;

  void *__object() const { return Object; }
  const CNxtIfaceWitness<T> *__witness() const { return Witness; }
};

int counterNextThunk(void *Self) {
  return static_cast<Counter *>(Self)->next();
}

Result benchmarkDirectDispatch(const Options &Opts) {
  Counter Value;
  return {"direct_dispatch",
          measure(Opts, [&] { consume(static_cast<std::uint64_t>(Value.next())); })};
}

Result benchmarkWitnessDispatch(const Options &Opts) {
  Counter Value;
  using DispatchEntry = int (*)(void *);
  const DispatchEntry Table[] = {counterNextThunk};
  const CNxtIfaceWitness<CounterLikeTag> Witness{
      static_cast<const void *>(Table)};
  const CNxtIfaceBorrowed<CounterLikeTag> View{&Value, &Witness};

  return {"witness_dispatch",
          measure(Opts, [&] {
            auto *FnTable =
                static_cast<const DispatchEntry *>(View.__witness()->Table);
            consume(static_cast<std::uint64_t>(FnTable[0](View.__object())));
          }),
          "direct_dispatch"};
}

void attachRatios(std::vector<Result> &Results) {
  auto lookup = [&](std::string_view Name) -> double {
    for (const Result &R : Results) {
      if (R.Name == Name)
        return R.NsPerIteration;
    }
    return 0.0;
  };

  for (Result &R : Results) {
    if (R.Baseline.empty())
      continue;
    double Baseline = lookup(R.Baseline);
    if (Baseline > 0.0)
      R.RatioToBaseline = R.NsPerIteration / Baseline;
  }
}

void printText(const Options &Opts, const std::vector<Result> &Results) {
  std::cout << std::fixed << std::setprecision(2);
  std::cout << "iterations=" << Opts.Iterations
            << " warmup=" << Opts.WarmupIterations << "\n";
  std::cout << std::left << std::setw(32) << "benchmark" << std::right
            << std::setw(14) << "ns/iter" << std::setw(22) << "baseline"
            << std::setw(12) << "ratio" << "\n";
  for (const Result &R : Results) {
    std::cout << std::left << std::setw(32) << R.Name << std::right
              << std::setw(14) << R.NsPerIteration << std::setw(22)
              << (R.Baseline.empty() ? "-" : R.Baseline) << std::setw(12);
    if (R.RatioToBaseline == 0.0) {
      std::cout << "-";
    } else {
      std::cout << R.RatioToBaseline << "x";
    }
    std::cout << "\n";
  }
  std::cout << "sink=" << Sink
            << " destructions="
            << DestructionCount.load(std::memory_order_relaxed) << "\n";
}

void printJson(const Options &Opts, const std::vector<Result> &Results) {
  std::cout << "{\n";
  std::cout << "  \"iterations\": " << Opts.Iterations << ",\n";
  std::cout << "  \"warmup_iterations\": " << Opts.WarmupIterations << ",\n";
  std::cout << "  \"benchmarks\": [\n";
  for (std::size_t I = 0; I < Results.size(); ++I) {
    const Result &R = Results[I];
    std::cout << "    {\n";
    std::cout << "      \"name\": \"" << R.Name << "\",\n";
    std::cout << "      \"ns_per_iteration\": " << std::fixed
              << std::setprecision(4) << R.NsPerIteration << ",\n";
    if (R.Baseline.empty()) {
      std::cout << "      \"baseline\": null,\n";
      std::cout << "      \"ratio_to_baseline\": null\n";
    } else {
      std::cout << "      \"baseline\": \"" << R.Baseline << "\",\n";
      std::cout << "      \"ratio_to_baseline\": " << std::fixed
                << std::setprecision(4) << R.RatioToBaseline << "\n";
    }
    std::cout << "    }";
    if (I + 1 != Results.size())
      std::cout << ",";
    std::cout << "\n";
  }
  std::cout << "  ],\n";
  std::cout << "  \"sink\": " << Sink << ",\n";
  std::cout << "  \"destructions\": "
            << DestructionCount.load(std::memory_order_relaxed) << "\n";
  std::cout << "}\n";
}

} // namespace

int main(int argc, char **argv) {
  Options Opts = parseOptions(argc, argv);

  std::vector<Result> Results;
  Results.push_back(benchmarkStdUniqueDrop(Opts));
  Results.push_back(benchmarkRuntimeUniqueDrop(Opts));
  Results.push_back(benchmarkStdSharedCopy(Opts));
  Results.push_back(benchmarkRuntimeSharedCopy(Opts));
  Results.push_back(benchmarkStdWeakLockHit(Opts));
  Results.push_back(benchmarkRuntimeWeakLockHit(Opts));
  Results.push_back(benchmarkStdWeakLockMiss(Opts));
  Results.push_back(benchmarkRuntimeWeakLockMiss(Opts));
  Results.push_back(benchmarkDirectDispatch(Opts));
  Results.push_back(benchmarkWitnessDispatch(Opts));
  attachRatios(Results);

  if (Opts.Json) {
    printJson(Opts, Results);
  } else {
    printText(Opts, Results);
  }
  return 0;
}
