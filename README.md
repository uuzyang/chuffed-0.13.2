# Chuffed, a lazy clause generation solver 

Geoffrey Chu, Peter J. Stuckey, Andreas Schutt, Thorsten Ehlers, Graeme Gange, Kathryn Francis

Data61, CSIRO, Australia

Department of Computing and Information Systems
University of Melbourne, Australia

## Usage

The easiest way to use Chuffed is as a backend to the [MiniZinc constraint modelling language](http://www.minizinc.org). Compiling Chuffed using the
instructions below will create the `fzn-chuffed` executable that can interpret
MiniZinc's FlatZinc solver language.

You can also use Chuffed directly from C++. Take a look at the files in the
`examples` folder to get started.

### Assumption interface
Chuffed has FlatZinc hooks to the internal assumption handling. By adding an
`assume(array [int] of var bool)` annotation to a solve item, the specified Booleans
will be treated as assumptions. This annotation can be used when chuffed's solver
specific definitions are included (i.e., by adding `include "chuffed.mzn";` to your
MiniZinc model).

If the resulting problem is unsatisfiable (or the optimum is found), the solver will
print a valid -- though not necessarily minimal -- nogood in terms of assumptions
(and, for optimization instances, an objective bound).

### Integration with CP Profiler

The *CP Profiler*, integrated into the
[MiniZincIDE](https://github.com/MiniZinc/MiniZincIDE), can be used with Chuffed
to visualise the search trees and analyse the nogoods that Chuffed explores when
solving a problem. In order to enable profiling support, Chuffed includes
profiler connection code. This has been included as a git subtree in
`thirdparty/cp-profiler-integration`. To pull the newest version of the
integration code, use the following command in the repository root.

```
git subtree pull --prefix thirdparty/cp-profiler-integration https://github.com/MiniZinc/cpp-integration.git master --squash
```

### Command-Line Options

Chuffed supports various CLI parameters to control search strategy, restart behavior, and heuristics. Key options include:

#### Search & Heuristic Options
- `--var-heuristic <name>`: Select variable selection heuristic. Supported values:
  - `activity` or `vsids`: Activity-based (default)
  - `input_order`: Choose variables in input order
  - `first_fail`: Choose variable with smallest domain
  - `random`: Random variable selection
  - `occurrence`: Choose most frequently used variable
  - And others: `anti_first_fail`, `smallest`, `largest`, `most_constrained`, `max_regret`

- `--val-heuristic <name>`: Select value assignment heuristic. Supported values:
  - `min`: Choose minimum value (default)
  - `max`: Choose maximum value
  - `default`: Use default behavior
  - `median`: Choose median value
  - `split_min`, `split_max`: Bisection-based value selection

#### Restart Strategy Options
- `--restart <type>`: Set restart strategy (`chuffed_default`, `none`, `constant`, `linear`, `luby`, `geometric`)
- `--restart-scale <n>`: Conflict count before restart (default: 1000000000)
- `--restart-base <n>`: Base for geometric restart sequence (default: 1.5)
- `--toggle-vsids [on|off]`: Alternate between search annotation and VSIDS during restarts
- `--switch-to-vsids-after <n>`: Switch to VSIDS after N conflicts

#### Adaptive Restart Options
- `--adaptive-restart [on|off]`: Enable Choco-style adaptive restart with probing and subtree revisit
- `--adaptive-restart-top-k <n>`: Keep top K subtree candidates for revisit (default: 5)
- `--adaptive-restart-probe-limit <n>`: Number of probing restarts before revisit phase (default: 3)
- `--adaptive-restart-bound-rate <n>`: Growth rate for revisit selection bounds (default: 1.5)
- `--adaptive-restart-seed <n>`: Random seed for adaptive restart (default: 0)
- `--adaptive-roulette <n>`: Roulette power for weighted subtree selection (default: 1.0)
  - When `1.0`: proportional selection by bound span
  - When `> 1.0`: favor candidates with larger bounds more heavily
  - When `< 1.0`: flatten the distribution

#### Example Usage
```bash
# Standard search with activity-based heuristics and geometric restarts
fzn-chuffed --var-heuristic activity --val-heuristic min --restart geometric model.fzn

# Adaptive restart with custom parameters
fzn-chuffed --adaptive-restart on --var-heuristic activity --adaptive-restart-top-k 10 \
  --adaptive-restart-probe-limit 5 --adaptive-roulette 1.5 model.fzn

# Luby restart with random value selection
fzn-chuffed --restart luby --val-heuristic random model.fzn
```

### Adaptive Restart Implementation

Chuffed implements a Choco-inspired adaptive restart mechanism that combines probing and subtree revisit strategies:

#### High-Level Algorithm
1. **Probing Phase**: Perform a fixed number of restarts (`adaptive_restart_probe_limit`) while collecting decision subtrees.
   - At each restart, extract the current decision path and compute a "score" based on variable domain sizes.
   - Keep the top-K highest-scoring subtrees in a candidate pool.

2. **Revisit Phase**: After probing completes, switch to revisiting promising subtrees.
   - Select one of the K candidate subtrees using a weighted roulette selection.
   - Continue with normal search from that subtree, allowing exploration of alternative branches.

3. **Subtree Scoring**: The score of a subtree is computed as the count of variables with remaining alternatives (domain size > 1) after the decisions are made.
   - Higher score = more freedom to explore, indicating a potentially better branching point.

4. **Weighted Roulette Selection**: Subtrees are selected probabilistically:
   - Each candidate is assigned a weight based on the geometric series used to define selection bounds.
   - The weight is raised to the power of `adaptive_subtree_roulette` to adjust selection bias:
     - `1.0`: uniform weighting by bound span (recommended)
     - `> 1.0`: prefer larger-span (more promising) candidates more strongly
     - `< 1.0`: flatten the distribution toward uniform random selection

#### Integration with Restart Strategy
- The adaptive restart layer works **independently** of the restart type (`--restart`), though geometric restarts are recommended for better performance.
- After each restart, `engine.adaptive_restart_enabled`, `engine.adaptive_current_probe_num`, and `engine.adaptive_probe_limit` control the probe/revisit transition.
- The FlatZinc layer invokes `beforeRestart()` hook before resetting to root to capture the current subtree, and `onRestart()` after to set assumptions based on the selected revisit subtree.

#### Parameters & Tuning
- **`--adaptive-restart-top-k`**: Larger values keep more candidates (more diversification, higher memory).
- **`--adaptive-restart-probe-limit`**: Number of restarts to probe (more probes = better information, longer setup).
- **`--adaptive-restart-bound-rate`**: Controls the geometric series for selection bounds (higher = more bias toward top candidates).
- **`--adaptive-roulette`**: Fine-tunes the selection bias (see above).

## Compilation

Chuffed can be compiled on Windows, macOS and Linux.

#### Prerequisites

You need a recent C++ compiler that supports C++11 (e.g. Microsoft Visual Studio
2013, gcc 4.8, clang), as well as the CMake build tool (at least version 3.1).
To automatically format the Chuffed source code, the `clang-format` executable
must be available.

#### CMake & Co

To initialize the CMake build environment, using `build` as the build directory,
use the following command:

    cmake -B build -S .

To then build the `fzn-chuffed` executable run:

    cmake --build build

To install `fzn-chuffed` run the following command: 

    cmake --build build --target install
    
The installation directory can be chosen by appending
`-DCMAKE_INSTALL_PREFIX=$LOCATION` with the chosen location to the initial CMake
command.

To build the C++ examples:

    cmake --build build --target examples

To format the Chuffed source files

    cmake --build build --target format

## Description

Chuffed is a state of the art lazy clause solver designed from the ground up
with lazy clause generation in mind. Lazy clause generation is a hybrid
approach to constraint solving that combines features of finite domain
propagation and Boolean satisfiability. Finite domain propagation is
instrumented to record the reasons for each propagation step. This creates an
implication graph like that built by a SAT solver, which may be used to create
efficient nogoods that record the reasons for failure. These nogoods can be
propagated efficiently using SAT unit propagation technology. The resulting
hybrid system combines some of the advantages of finite domain constraint
programming (high level model and programmable search) with some of the
advantages of SAT solvers (reduced search by nogood creation, and effective
autonomous search using variable activities).

The FD components of Chuffed are very tightly integrated with a SAT solver. For
"small" variables (|D| <= 1000), SAT variables representing [x = v] or [x >= v]
are eagerly created at the start of the problem. Channelling constraints are
natively enforced by the variable objects in order to keep the FD solver and
the SAT solver's view of the domains fully consistent at all times. For "large"
variables (|D| > 1000), the SAT variables are lazily generated as needed. Every
propagator in Chuffed has been instrumented so that all propagation can be
explained by some combination of the literals in the SAT solver. An explanation
is of the form a_1 /\ ... /\ a_n -> d, where a_i represent domain restrictions
which are currently true, and d represents the domain change that is implied.
e.g. Suppose z >= x + y, and we have x >= 3, y >= 2. Then the propagator would
propagate z >= 5 with explanation clause x >= 3 /\ y >= 2 -> z >= 5.

The explanations for each propagation form an implication graph. This allows us
to do three very important things. Firstly, we can derive a nogood to explain
each failure. Such nogoods often allow us to avoid a very large amount of
redundant work, thus producing search trees which are orders of magnitude
smaller. Secondly, nogoods allow us to make informed choices about
non-chronological back-jumping. When no literal from a decision level appears
in the nogood, it is indicative of the fact that the decision made at that
level was completely irrelevant to the search. Thus by back-jumping over such
decisions, we retrospectively avoid making such bad decisions, and hopefully
make good decisions instead which drive the search towards failure. Thirdly, by
analysing the conflict, we can actively gain some information about what good
decision choices are. The Variable State Independent Decaying Sum (VSIDS)
heuristic is an extremely effective search heuristic for SAT problems, and is
also extremely good for a range of CP problems. Each variables has an
associated activity, which is increased whenever the variable is involved in
the conflict. Variables with the highest activity is chosen as the decision
variable at each node. The activities are decayed to reflect the fact that the
set of important variables changes with time.

Although Chuffed implements lazy clause generation, which is cutting edge and
rather complex, the FD parts of Chuffed are relatively simple. In fact, it is
quite minimalistic. Chuffed only supports 3 different propagator priorities.
Chuffed implements a number of global propagators (alldiff, inverse,
minimum, table, regular, mdd, cumulative, disjunctive, circuit, difference).
It also only supports two kinds of integer variables. Small integer variables
for which the domain is represented by a byte string.
And large integer variables for which the domain is represented only by its
upper and lower bound (no holes allowed). All boolean variables and boolean
constraints are handled by the builtin SAT solver.

Great pains have been taken to make everything as simple and efficient as
possible. The solver, when run with lazy clause generation disabled, is
somewhat comparable in speed with older versions of Gecode. The overhead from
lazy clause generation ranges from negligible to perhaps around 100%. The
search reduction, however, can reach orders of magnitude on appropriate
problems. Thus lazy clause generation is an extremely important and useful
technology. The theory behind lazy clause generation is described in much
greater detail in various papers.
