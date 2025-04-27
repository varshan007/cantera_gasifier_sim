import cantera as ct
import numpy as np
import streamlit as st
gas = ct.Solution('phase_reaction.yaml')

# --- User Inputs via Streamlit ---
st.title("Advanced Multi-Zone Gasifier Kinetic Model")
height = st.number_input("Gasifier Height (m)", value=1.5)
diameter = st.number_input("Gasifier Diameter (m)", value=0.4)
throat_diameter = st.number_input("Throat Diameter (m)", value=0.08)
feed_rate = st.number_input("Biomass Feed Rate (kg/hr)", value=50.0)
moisture = st.number_input("Moisture Content (% w.b.)", value=15.0)
zone_temps = {
    "drying": st.number_input("Drying Zone Temp (K)", value=423),
    "pyrolysis": st.number_input("Pyrolysis Zone Temp (K)", value=773),
    "oxidation": st.number_input("Oxidation Zone Temp (K)", value=1223),
    "reduction": st.number_input("Reduction Zone Temp (K)", value=1073)
}

# --- Define Reaction Mechanisms for Each Zone ---
# You must create or adapt suitable mechanisms for your feedstock!
# Example: "biomass_gasification.yaml"
gas = ct.Solution("biomass_gasification.yaml")  # Custom mechanism required

# --- Zone 1: Drying (Batch Reactor) ---
gas.TPX = zone_temps["drying"], ct.one_atm, "BIOMASS:1.0, H2O:0.15"
drying_reactor = ct.IdealGasReactor(gas, energy='on', volume=0.1)
drying_net = ct.ReactorNet([drying_reactor])
drying_net.advance(10)  # Simulate for 10 s (adjust as needed)

# --- Zone 2: Pyrolysis (Batch Reactor) ---
gas.TPX = zone_temps["pyrolysis"], ct.one_atm, "DRY_BIOMASS:1.0"
pyrolysis_reactor = ct.IdealGasReactor(gas, energy='on', volume=0.1)
pyrolysis_net = ct.ReactorNet([pyrolysis_reactor])
pyrolysis_net.advance(10)

# --- Zone 3: Oxidation (CSTR) ---
gas.TPX = zone_temps["oxidation"], ct.one_atm, "VOLATILES:1.0, O2:0.21, N2:0.79"
oxidation_reactor = ct.IdealGasReactor(gas, energy='on', volume=0.1)
oxidation_net = ct.ReactorNet([oxidation_reactor])
oxidation_net.advance(10)

# --- Zone 4: Reduction (Plug Flow or Batch Reactor) ---
gas.TPX = zone_temps["reduction"], ct.one_atm, "CHAR:1.0, CO2:0.1, H2O:0.1"
reduction_reactor = ct.IdealGasReactor(gas, energy='on', volume=0.1)
reduction_net = ct.ReactorNet([reduction_reactor])
reduction_net.advance(10)

# --- Collect and Display Results ---
st.subheader("Zone Outputs (Mole Fractions)")
st.write("Drying Zone Products:", drying_reactor.thermo.X)
st.write("Pyrolysis Zone Products:", pyrolysis_reactor.thermo.X)
st.write("Oxidation Zone Products:", oxidation_reactor.thermo.X)
st.write("Reduction Zone Products:", reduction_reactor.thermo.X)

# --- Calculate Syngas Yield, CGE, Flow Rate, Residence Time ---
# Use Cantera's built-in functions and your reactor volumes/flows
# Example for syngas composition after reduction:
syngas_comp = reduction_reactor.thermo.X
syngas_yield = np.sum([syngas_comp[gas.species_index(s)] for s in ["CO", "H2", "CH4"]])
st.write(f"Syngas Yield (mole fraction): {syngas_yield:.3f}")

# Residence time estimation (simplified)
gasifier_vol = np.pi * (diameter/2)**2 * height
syngas_flow_m3s = feed_rate / 3600  # Placeholder; use actual syngas flow
res_time = gasifier_vol / syngas_flow_m3s
st.write(f"Estimated Residence Time: {res_time:.2f} s")

# CGE, etc., can be calculated using enthalpy and LHV from Cantera

st.info("This model uses multi-zone kinetic simulation with Cantera. For best results, provide a detailed reaction mechanism for your specific biomass and operating conditions.")
