import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.style.use('style.mplstyle')

# healthy, infected, immune, dead
personStateColors = ['#404040', '#ff0000', '#00ff00', '#000000']

# sets graph title
def ax2Title(ax2):
	ax2.set_title('number of infected')

# updates figure with common values across all simulations
def figUpdate(ax1, ax2, x_plot, y_plot):
	ax1.set_xlim(x_plot[0], x_plot[1])
	ax1.set_ylim(y_plot[0], y_plot[1])
	ax1.axis('off')
	ax2Title(ax2)

# initialises figure with common values across all simulations
def figInit(xbounds, ybounds, pop_size):
	fig = plt.figure(figsize=(5,7))
	spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])

	ax1 = fig.add_subplot(spec[0,0])
	ax1.axis('off')
	plt.title('infection simulation')
	plt.xlim(xbounds[0], xbounds[1])
	plt.ylim(ybounds[0], ybounds[1])

	ax2 = fig.add_subplot(spec[1,0])
	ax2Title(ax2)
	#ax2.set_xlim(0, simulation_steps)
	ax2.set_ylim(0, pop_size + 100)

	return fig, ax1, ax2