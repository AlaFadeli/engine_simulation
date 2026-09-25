# Car Engine Simulator Architecture Plan

## 1. Project Direction

The first version will be a command-line engine simulator. It will focus on deterministic physics, readable output, and testability. A graphical dashboard can be added later without coupling it to the simulation core.

Primary goals:

- Simulate engine speed, torque, fuel consumption, cylinder behavior, and thermal state.
- Keep physics independent from command-line input and output.
- Use SI units internally.
- Run fixed-step physics independently of the CLI refresh rate.
- Support deterministic replay and automated testing.
- Make calibration data replaceable without rewriting the engine core.

Initial CLI responsibilities:

- Parse commands and options.
- Create or load engine configuration.
- Start, pause, stop, and step the simulation.
- Apply throttle, brake, and fuel commands.
- Display telemetry at a configurable interval.
- Export telemetry for later analysis.

The CLI must not calculate engine physics. It should send commands to the application layer and render returned state or snapshots.

## 2. Proposed Project Structure

The project should use a standard `src` layout:

```text
engine_simulator/
├── config.json
├── main.py
├── plan.md
├── src/
│   ├── __init__.py
│   ├── application.py
│   ├── cli.py
│   ├── config.py
│   ├── models.py
│   ├── engine.py
│   ├── cylinder.py
│   ├── crankshaft.py
│   ├── fuel_system.py
│   ├── cooling_system.py
│   ├── controls.py
│   ├── environment.py
│   ├── load.py
│   ├── faults.py
│   ├── telemetry.py
│   └── physics/
│       ├── __init__.py
│       ├── geometry.py
│       ├── thermodynamics.py
│       ├── friction.py
│       ├── thermal.py
│       └── integration.py
└── tests/
    ├── test_geometry.py
    ├── test_thermodynamics.py
    ├── test_crankshaft.py
    ├── test_fuel_system.py
    ├── test_cooling_system.py
    ├── test_integration.py
    ├── test_determinism.py
    └── test_cli.py
```

`main.py` is the only project-root Python entry point. All authoritative implementation modules live under `src/`. The empty root modules `engine.py`, `physics.py`, and `dashboard.py` are legacy placeholders and should not be part of the target architecture. A future dashboard can be added under `src/` or as a separate top-level application only when that feature is introduced.

Recommended execution path:

```text
main.py → src.cli → src.application → src.engine → subsystems → physics
```

`dashboard.py` should not be part of the initial CLI simulation path. It can remain a future extension point.

## 3. Layered Architecture

### Presentation Layer

Files:

- `main.py`
- `src/cli.py`
- Future `src/dashboard.py` or a separate dashboard package

Responsibilities:

- Parse command-line arguments.
- Read keyboard or scripted commands.
- Format telemetry.
- Handle pause, resume, step, and exit commands.
- Never mutate engine components directly.

The CLI should communicate through an application service rather than reaching into `Engine`, `FuelSystem`, or `Crankshaft`.

### Application Layer

File:

- `src/application.py`

Responsibilities:

- Own the simulation clock and fixed-step accumulator.
- Translate input commands into immutable control snapshots.
- Call the engine once per physics step.
- Collect telemetry snapshots.
- Coordinate CLI output frequency.
- Enforce command-level validation such as valid ranges and valid engine states.

The application layer is the only layer that should coordinate the wall clock, simulation time, and user commands.

### Domain Layer

Files:

- `src/engine.py`
- `src/cylinder.py`
- `src/crankshaft.py`
- `src/fuel_system.py`
- `src/cooling_system.py`
- `src/load.py`
- `src/faults.py`

Responsibilities:

- Represent the engine and its physical state.
- Implement subsystem behavior.
- Maintain ownership of mutable state.
- Exchange explicit state and result objects.
- Apply physical limits and generate fault events.

### Physics Layer

Directory:

- `src/physics/`

Responsibilities:

- Engine geometry.
- Piston kinematics.
- Pressure-volume behavior.
- Combustion energy release.
- Heat transfer.
- Friction and pumping losses.
- Torque and power conversion.
- Numerical integration.
- Unit conversions and numerical safety checks.

Physics functions should be pure wherever possible. They should calculate a result from inputs rather than mutating another subsystem.

### Data and Configuration Layer

Files:

- `src/config.py`
- `src/models.py`
- `src/telemetry.py`

Responsibilities:

- Immutable engine and simulation configuration.
- Typed mutable state owned by components.
- Immutable control and telemetry snapshots.
- Runtime history buffers and derived indicators.
- Fault and event records.

## 4. Core Object Model

### Engine

`Engine` is the aggregate and composition root. It owns:

- One crankshaft.
- A list of cylinders.
- One fuel system.
- One cooling system.
- One load model.
- One fault collection.
- One engine configuration reference.

`Engine` coordinates updates and aggregates subsystem results. It does not implement every physical equation itself.

### Cylinder

Each cylinder owns:

- Crank phase and stroke.
- Piston position and velocity.
- Cylinder volume.
- Charge mass and composition.
- Cylinder pressure and gas temperature.
- Burned-fuel mass and burn fraction.
- Wall temperature and heat transfer state.
- Cylinder friction and pumping state.

A cylinder returns pressure, force, indicated torque, and heat rejected. It must not directly change crankshaft speed, fuel-tank state, or coolant state.

### Crankshaft

The crankshaft owns:

- Crank angle.
- Angular velocity.
- Equivalent rotational inertia.
- Accumulated indicated torque.
- Mechanical loss and load integration.
- Optional flywheel or drivetrain coupling state.

All cylinders use the same crankshaft angle. Firing order is represented by cylinder phase offsets relative to that shared angle.

### FuelSystem

The fuel system owns:

- Tank fuel mass.
- Fuel type and lower heating value.
- Fuel density and stoichiometric ratio.
- Injector state and duty cycle.
- Fuel pressure.
- Vaporization and transport-delay state.
- Per-cylinder delivered fuel mass.

It returns fuel delivery results but does not calculate pressure, torque, or coolant state.

### CoolingSystem

The cooling system owns:

- Coolant temperature and mass.
- Engine block temperature.
- Optional oil temperature.
- Coolant flow.
- Thermostat state.
- Radiator heat rejection.
- Thermal capacity and overheat state.

It receives cylinder heat loss and returns a thermal boundary to each cylinder. It does not directly control fuel delivery or mechanical rotation.

## 5. State and Dependency Rules

Use immutable data for:

- Engine configuration.
- CLI command results.
- Control snapshots.
- Telemetry snapshots.
- Fault records.

Use mutable data only for state owned by the active subsystem.

Dependency direction:

```text
CLI → Application → Engine → Subsystems → Physics
                         ↓
                  Models / Telemetry
```

Rules:

- The crankshaft is the single source of angular velocity and crank angle.
- The application layer is the only clock owner.
- The dashboard or CLI never calls low-level physics functions.
- Subsystems communicate through explicit inputs and return values.
- No subsystem keeps a mutable reference to the full engine.
- No physics helper reaches back into another subsystem.
- No global engine state is used.

## 6. Physics Architecture

### Engine Geometry

For bore `B`, stroke `L`, connecting-rod length `a`, crank radius `r = L / 2`, clearance volume `V_c`, and crank angle `theta`:

- Swept volume per cylinder: `V_s = pi * B^2 * L / 4`.
- Total displacement: `V_d = cylinder_count * V_s`.
- Compression ratio: `(V_c + V_s) / V_c`.
- Cylinder volume is calculated from the slider-crank geometry.
- Piston position and velocity are calculated from the volume-position relationship.
- The effective connecting-rod moment arm is used to convert piston force to crank torque.

Geometry functions should be independent of engine class state so they can be tested directly.

### Fuel and Combustion

The initial model should support:

- Injector mass-flow rate.
- Fuel mass delivered per cylinder per step.
- Intake air estimate.
- Stoichiometric air-fuel ratio.
- Equivalence ratio.
- Lower heating value.
- Combustion efficiency.
- Burned-fuel fraction based on a Wiebe-like curve.
- Chemical energy released during the combustion event.

Chemical energy is based on burned fuel mass, fuel lower heating value, and combustion efficiency. Fuel delivery and vaporization can initially be combined, but their interfaces should allow future separation.

### Cylinder Thermodynamics

The first cylinder model should combine:

- Intake and exhaust mass-flow approximations.
- Polytropic or ideal-gas pressure behavior.
- Combustion heat release.
- Cylinder-wall heat transfer.
- Residual gas handling.
- Pumping-work estimation.

The model should evolve pressure and temperature over time rather than deriving all behavior only from a torque lookup table. Lookup tables can be used as calibration or fallback data later.

### Mechanical Dynamics

For every fixed step:

```text
net torque = indicated torque
           - friction torque
           - pumping torque
           - accessory torque
           - external load torque
```

Rotational dynamics are based on:

```text
equivalent inertia × angular acceleration = net torque
```

Derive RPM from angular velocity and brake power from brake torque and angular velocity.

### Friction

Start with a deterministic model containing:

- Constant bearing and seal loss.
- Viscous speed-dependent loss.
- Quadratic speed-dependent loss.
- Optional temperature correction.

Use guards near zero angular velocity. Later versions may replace the polynomial with calibrated maps.

### Thermal Dynamics

Use lumped thermal states for:

- Cylinder gas.
- Cylinder wall.
- Engine block.
- Coolant.
- Optional oil.

Cylinder heat transfer depends on gas-to-wall temperature difference and effective heat-transfer area. Coolant energy is calculated from incoming coolant energy, heat received from the engine, radiator rejection, and pump or thermostat effects.

The thermal model should return a boundary state to the cylinder while retaining ownership of coolant and block temperatures.

## 7. Fixed-Step Simulation Loop

The CLI may refresh at any display rate, but physics must run at a fixed rate.

Application-loop sequence:

1. Read a monotonic timestamp.
2. Calculate elapsed frame time.
3. Clamp the elapsed time after pauses or stalls.
4. Parse and validate user commands.
5. Add elapsed time to a physics accumulator.
6. Execute zero or more fixed physics steps.
7. Limit catch-up steps per display frame.
8. Record or discard excess accumulated time according to a defined policy.
9. Format and display telemetry when the display interval is reached.
10. Continue until exit, end of scripted input, or engine stop.

The engine should expose a single-step transition. It must not know whether it was called by a CLI, test, or future graphical application.

### Fixed Step

For a physics frequency `f`:

```text
physics_dt = 1 / f
```

Use a smaller internal substep for cylinder thermodynamics if required. Keep the outer simulation timestep fixed and deterministic.

### Integration

A semi-implicit update is appropriate for the crankshaft:

1. Compute torque and angular acceleration from the current state.
2. Update angular velocity.
3. Update crank angle using the new angular velocity.

Required protections:

- Cylinder volume must remain positive.
- Fuel mass must remain nonnegative.
- Temperatures and pressures must remain finite.
- Angular velocity must be bounded.
- Crank angle must wrap consistently.
- Zero-speed and zero-fuel cases must be handled explicitly.
- Persistent invalid values should create faults rather than silently resetting state.

## 8. CLI Architecture

The CLI should support a simple interactive mode and a scripted mode.

### Interactive commands

Conceptual commands should include:

- `start`: begin simulation.
- `pause`: stop advancing physics without losing state.
- `resume`: continue simulation.
- `step`: advance exactly one fixed physics step.
- `throttle <value>`: set desired throttle.
- `brake <value>`: set desired brake or load.
- `fuel-cut`: disable fuel delivery.
- `status`: print current telemetry.
- `telemetry`: print a more detailed state snapshot.
- `config`: show active configuration.
- `reset`: restore the initial engine state.
- `help`: show available commands.
- `exit`: stop the application.

The exact command names can change, but commands should map to application-level actions rather than direct subsystem mutation.

### Scripted mode

The simulator should be able to run without interactive input. A scenario should define:

- Duration.
- Physics frequency.
- Display frequency.
- Initial engine state.
- Throttle, brake, and fuel commands over time.
- Optional environment and load conditions.
- Output format and destination.

This makes the project useful for automated tests and later calibration.

## 9. Telemetry Contract

The engine or application produces immutable telemetry snapshots. Initial fields should include:

- Simulation time.
- Physics-step number.
- Crank angle.
- RPM.
- Angular velocity.
- Indicated torque.
- Brake torque.
- Net torque.
- Indicated and brake power.
- Fuel flow and total fuel consumed.
- Air-fuel ratio and equivalence ratio.
- Thermal efficiency.
- Per-cylinder pressure, temperature, piston position, and burn fraction.
- Coolant, block, and oil temperature.
- Maximum cylinder temperature.
- Heat rejected to coolant.
- Active warnings and faults.

The CLI formatter should consume snapshots and never inspect mutable engine internals. A future dashboard should use the same contract.

## 10. Faults and Operating Modes

Support the following operating modes:

- Cranking.
- Idle.
- Part load.
- Wide-open throttle.
- Deceleration fuel cut.
- Engine stop.
- Overspeed.
- Fuel starvation.
- Lean or rich operation.
- Overheating.
- Knock warning.

Fuel cut should remove chemical energy without directly setting RPM to zero. Engine stopping should normally emerge from load, clutch, and friction behavior. Explicit reset or test commands may override state.

## 11. Implementation Phases

### Phase 1: CLI and project foundation

- Create the `src` package.
- Establish package entry points and command parsing.
- Define configuration, state, controls, telemetry, and fault types.
- Establish SI constants and configuration validation.
- Create basic test organization.

### Phase 2: Mechanical simulation

- Implement engine geometry and slider-crank motion.
- Implement crank-angle wrapping and cylinder phasing.
- Implement crankshaft inertia and torque integration.
- Add basic friction and external load.
- Verify free acceleration and loaded equilibrium.

### Phase 3: Fuel and combustion

- Add fuel tank and injector behavior.
- Add fuel delivery to each cylinder.
- Add air-fuel and equivalence-ratio calculations.
- Add burn fraction and chemical energy release.
- Add cylinder pressure, piston force, and indicated torque.
- Add fuel, power, and efficiency telemetry.

### Phase 4: Thermal behavior

- Add cylinder-wall heat transfer.
- Add block and coolant energy balances.
- Add radiator and thermostat behavior.
- Add warm-up, steady-state, and overheating scenarios.
- Add temperature-dependent friction correction.

### Phase 5: Determinism and validation

- Add fixed-step determinism tests.
- Add rendering-rate independence tests.
- Add numerical-stability tests for low and high RPM.
- Add tests for fuel starvation, fuel cut, and invalid configuration.
- Verify that identical input sequences produce identical state sequences.

### Phase 6: Advanced models

- Add calibrated torque and friction maps.
- Add richer ignition timing and burn duration.
- Add intake and exhaust pressure dynamics.
- Add turbocharger and drivetrain models.
- Add knock and oil-temperature models.
- Preserve compatibility with the CLI and telemetry contract.

## 12. Testing Strategy

### Unit tests

- Geometry and cylinder volume.
- Piston position, velocity, and moment arm.
- Crank-angle conversion and wrapping.
- Fuel delivery and tank consumption.
- Air-fuel ratio and equivalence ratio.
- Burn fraction and heat release.
- Pressure and temperature behavior.
- Friction and torque sign conventions.
- Thermal transfer.
- RPM, power, and efficiency conversion.
- Configuration and command validation.

### Integration tests

- Fuel delivery to combustion energy.
- Cylinder pressure to crankshaft torque.
- Cylinder heat to coolant temperature.
- Load to RPM equilibrium.
- Throttle changes and acceleration.
- Fuel cut during deceleration.
- Warm-up and overheating.
- Pause, resume, step, reset, and exit commands.

### Determinism tests

- Run the same fixed-step scenario twice and compare state sequences.
- Run with different CLI display frequencies and confirm identical physics states.
- Confirm that command timing is interpreted relative to simulation time rather than display time.

### Stability tests

- High RPM with no load.
- Very low RPM.
- Abrupt throttle changes.
- Complete fuel starvation.
- Full load followed by fuel cut.
- Extreme ambient temperatures.
- Overheating.
- Invalid configuration values.

## 13. Acceptance Criteria

The CLI architecture is ready when:

- `src/` contains the authoritative simulation implementation.
- The CLI can start, pause, step, control, inspect, reset, and exit the simulator.
- The CLI does not contain physics formulas.
- The application layer owns the fixed-step clock.
- The crankshaft is the single source of rotational state.
- Cylinders cannot directly mutate global engine state.
- Telemetry is exposed through snapshots.
- Configuration and commands are validated.
- Fixed-step simulation is deterministic.
- Tests cover the main mechanical, fuel, thermal, and CLI paths.
- A future dashboard can consume the same application and telemetry interfaces without changing the physics core.
