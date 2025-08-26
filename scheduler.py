import clr
clr.AddReference(r'LibreHardwareMonitorLib') 
from LibreHardwareMonitor.Hardware import Computer

class Scheduler:
    def __init__(self, frequency):
        # frequency defined in seconds
        self.frequency = frequency
        self.c = Computer()

        self.c.IsCpuEnabled  = True
        self.c.IsGpuEnabled = True

    def getCPUMetrics(self):
        # CPU metrics can only be gathered in Admin mode
        data = []
        cpu = self.c.Hardware[0]
        cpuSensor = self.c.Hardware[0].Sensors
        
        for sensor in cpuSensor:
            if "Temperature" in str(sensor.SensorType):
                data.append({
                    'name':sensor.Name,
                    'value':sensor.Value
                })
                print('temp:', sensor.Name, ":", sensor.Value)
                cpu.Update()

        return data

    def getGPUMetrics(self):
        data = []
        gpu = self.c.Hardware[1]
        gpuSensor = self.c.Hardware[1].Sensors
        
        for sensor in gpuSensor:
            if "Temperature" in str(sensor.SensorType):
                data.append({
                    'name':sensor.Name,
                    'value':sensor.Value
                })
                print('temp:', sensor.Name, ":", sensor.Value)
                gpu.Update()

        return data

    def fetch(self):
        self.c.Open()
        
        CPUInfo = self.getCPUMetrics()
        GPUInfo = self.getGPUMetrics()

        return {'CPU_temp': CPUInfo, 'GPU_temp': GPUInfo}