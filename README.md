# Python COVID-19 ('Corona Virus') Simulation

![covid-19 sim!](images/covidsim.gif)

After seeing [this article](https://www.washingtonpost.com/graphics/2020/world/corona-simulator/) in the Washington Post I started wondering how such simulations might be done in Python, and indeed if I could expand upon the idea and make it more realistic.

For a moment I thought about writing the simualation itself in pure Python, with matplotlib as visualisation tool. However for large interacting populations, required computations scale quickly. Speeding up means reducing the operations to vector and matrix computations, something that can be done extremely efficiently through [NumPy](https://numpy.org/), which uses both a fast backend written in C, as well as makes use of hardware acceleration features like SIMD (single instruction, multiple data), which enables many operations on data arrays in relatively few clock cycles.

Aside from that, I've worked with NumPy a lot but felt there was still much to learn, so the challenge became: build such a simulation and improve upon it **using only NumPy** for the computations and matplotlib for the visualisation.


# Simulation runs

## Index
- [Simple infection simulation](#simple-infection-simulation)
- [Simulating Age Effects and Health Care Capacity](#simulating-age-effects-and-health-care-capacity)
	- [Case: 'Business As Usual'](#case-'business-as-usual')
	- [Case: 'Reduced Interaction'](#case-'reduced-interaction')
	- [Case: 'Lock-Down'](#case-'lock-down')
	- [Case: 'Self-Isolation'](#case-'self-isolation')
	- [Self-Isolation in Detail](#self-isolation-in-detail)
	
	
**For reproducibility of all simulations, numpy's seed has been set to '100' unless otherwise specified**

## Summary video
A video highlighting some of the scenarios [can be viewed here](http://www.paulvangent.com/covid/Covid_Compilation_reinfection.mp4)

## Simple Infection Simulation
As a first step I built a simulation of a population of randomly moving people. The people stay within the world bounds and each tick there's a 2% chance of them changing heading and speed. There's a 3% chance of becoming sick when getting close to an infected person, and a 2% chance of a fatal ending. **Click the image to view the video**

<a href="http://www.paulvangent.com/covid/Simple_Simulation.mp4">
<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/horizontal/simple_simulation.png" alt="image of the simuation">
</a>

See [simple_simulation.py](simple_simulation.py) for the code.

As you can see the virus managed to spread really quickly and almost got infected. In the end there were 44 fatalities, which is expected with a mortality rate of 2%.


## Simulating Age Effects and Health Care Capacity
Reality is of course more complex. Let's incorporate increasing risks with age, as well as a simple representation of a limited capacity healthcare system. Both affect mortality during a pandemic: the elderly are vulnerable, and once the healthcare system becomes overwhelmed a lot of people are at increased risk of dying due to lack of treatment. The following parameters are active (all are or course settable):

- the population's age follows a gaussian with a mean 55, SD of 1/3 the mean, and max of 105
- population consists of 2000 individuals
- there is a 3% chance of becoming infected when being near an infected person
- baseline mortality is 2%
- mortality chances start increasing at age 55, going up exponentially up to 10% at age 75 and beyond
- healthcare capacity is 300 beds
- when in medical treatment: mortality chance is halved
- when _not_ in medial treatment: mortality chance increases threefold. 
	- ***note*** that this affects the elderly disproportionally as their baseline risk is already higher to start with.

### Case 'Business As Usual'

See [simulation.py](simulation.py) for the code and settable parameters.

The first simuation run shows a population that simply keeps doing their normal thing and moving around. **Click the image to view the video.**

As you can see in the simulation still below, the healthcare system becomes completely overwhelmed, leading to 215 fatalities (10.75% of the population). 

<a href="http://www.paulvangent.com/covid/LimitedHealthcare_FastSpread.mp4">
<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/horizontal/lowcapacity_fastmovement.png" alt="image of the simuation">
</a>

### Case 'Reduced Interaction'

The second simulation has the same settings, but to simulate people staying at home whenever possible and only going out when they have to, mobilty is greatly reduced. **Click the image to view the video.**

As you can see in this simulation, while at some point healthcare capacity was overasked, the effects on mortality remain low at 58 fatal endings in this run (2.9%). That's almost 4x less fatalities.

<a href="http://www.paulvangent.com/covid/LimitedHealthcare_SlowMobility.mp4">
<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/horizontal/lowcapacity_slowmovement.png" alt="image of the simuation">
</a>


### Case 'Lock-Down'
Let's simulate a lock-down once 5% of the population is infected. To simulate this, we will make 90% of the people stop moving once locked-down, the remaining 10% will move with substantially reduced speed to simulate them being more cautious. This 10% represents the professions that are considered critical to society: these people will still be on the move and in contact with other people even in a lock-down. Another part of the 10% comes from people being people, meaning no lock-down will be perfect as there will always be those breaking quarantine. **Click the image to view the video.**

<a href="http://www.paulvangent.com/covid/lockdown_90percent.mp4">
<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/horizontal/lockdown_90percent.png" alt="image of the simuation">
</a>

Notice that once locked-down, the number of infections still increases for some time. This happens because of some of the healthy people will be locked into the same household with infected people, and thus become infected relatively quickly as well. If one of the moving population members (perhaps a mail man or someone delivering groceries) infects one of a cluster of people locked down together, the disease might spread. This leads to small and isolated outbreaks, which are contained very well through the lock-down.

However, if the lock down is lifted and a new case is introduced, a potential deadly situation quickly develops if no adequeate measures are taken:

<a href="http://www.paulvangent.com/covid/lockdown_90percent_reinfect.mp4">
<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/horizontal/lockdown_reinfection.png" alt="image of the simuation">
</a>

**In such a situation repeated lock-downs seem inevitable if the infection keeps returning.**

### Case 'Self-Isolation'

Another approach is self-isolation: instructing people who have symptoms to stay at home. This was the initial approach the Dutch government had taken and is the approach in many countries that are not locked down. How effective is such a measure, especially given that not everybody will (or can) follow it? [It turns out people can be infectious to others without manifesting symptoms](https://edition.cnn.com/2020/03/14/health/coronavirus-asymptomatic-spread/index.html), which further complicates such a 'stay home if you feel ill' scenario.

In the simulation, people who are infected will self-isolate. Those traveling to the isolation area can not infect others anymore, to simulate that these people are aware of their infection and will take precautions not to infect others. **Click the image to view the video.**

<a href="http://www.paulvangent.com/covid/Self_Isolation.mp4">
<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/horizontal/self-isolation.png" alt="image of the simuation">
</a>


### Self-Isolation in Detail

The picture here is more complex, as factors such as population density and the percentage of people that break the voluntary quarantaine have a large effect. Let's run the simulation with three population densities ('high': 2000 people on a 1x1 area, 'medium': 2000 people on a 1.5x1.5 area, and 'low': 2000 people on 2x2 area), and let's simulate different compliance percentages. Because the situation is based on randomness, let's do a monte carlo simulation with 100 iterations for each setting, so that we can be reasonably confident in our estimates:

*High population density*:

<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/selfisolation_high_100r.png" alt="high density graph" width="700">

*Medium population density:*

<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/selfisolation_medium_100r.png" alt="medium density graph" width="700">

*Low population density:*

<img align="center" src="https://github.com/paulvangentcom/python_corona_simulation/blob/master/images/selfisolation_low_100r.png" alt="medium density graph" width="700">


This illustrates the interaction between the density of the population (and thus how many people you come across per time unit), and the percentage of infectious people present in the population. This is what you would expect, as both of these factors affect your odds of running into an infected person. Notice how the plots show a clear 'tipping point': after 'n' number of infections, the virus spread starts accelerating. The peak amounf ot infections strongly depends on how many people obey the self-isolation rules. However, reports have been going around that [even without symptoms you can still be contagious](https://edition.cnn.com/2020/03/14/health/coronavirus-asymptomatic-spread/index.html), and [remain contagious for quite some time after recovering](https://www.cbsnews.com/news/coronavirus-can-live-in-your-body-for-up-to-37-days-according-to-new-study/), which makes such a self-isolation scenario risky in the case of COVID-19.




![logo](images/Logo_TUDelft.jpg)
