# TO-DO
- [X] refactor methods away into classes to make codebase less unwieldy
- [ ] Make package + dependencies installable, add simple installation guide
- ~~[ ] Add CuPy compatibility mode to utilize CUDA (NVidia GPU) for computations~~  
note: CuPy created major slowdowns, likely due to the large number of relatively small matrix operations, each of which requires moving data to and from GPU.
- [ ] Add NumBa support to speed up simulations without GPU
- [X] Plot S-I-R parameters
- [X] Beautify plotting
- [ ] Add travel behaviour (work, groceries, school)
- [ ] Add mechanic where recovered still carry viral load for settable period
- [ ] Prioritise health care based on risk profiles once capacity is reached
- [ ] Add Healthcare workers and simulate effects on healthcare effectiveness when they fall ill
- [ ] Add method for people to become reinfected with settable odds 
- [ ] Add plotting method that splits outcome according to age
- [ ] Implement S-I-R modeling to compare to agent-based approach
- [ ] Add scenario where the elderly are quarantined first when infections happen (u/ColCrabs & u/rataktaktaruken)
- [X] Speed up plotting
