from scheduler import Scheduler
import plotly.express as px
import time, asyncio

if __name__ == '__main__':
    schedule = Scheduler(1)
    
    temperatures = schedule.fetch()
    cpu_core_names = []
    cpu_core_temperatures = []

    gpu_core_names = []
    gpu_core_temperatures = []

    for values in temperatures['CPU_temp']:
        cpu_core_names.append(values['name'])
        cpu_core_temperatures.append(values['value'])

    for values in temperatures['GPU_temp']:
        gpu_core_names.append(values['name'])
        gpu_core_temperatures.append(values['value'])

    #fig = px.line(data_frame=temperatures['CPU_temp'], x=cpu_core_names, y=cpu_core_temperatures)
    #fig.show(renderer="browser")
