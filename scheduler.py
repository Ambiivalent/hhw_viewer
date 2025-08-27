import clr
clr.AddReference(r'LibreHardwareMonitorLib') 
from LibreHardwareMonitor.Hardware import Computer
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import dash
from dash import Dash, html, dcc, callback, Output, Input

class Scheduler:
    def __init__(self, frequency):
        # Frequency defined in seconds
        self.frequency = frequency
        self.c = Computer()
        self.c.IsCpuEnabled  = True
        self.c.IsGpuEnabled = True
        
        self.dataPoints = {}
        self.statistics = {
            "average": 0,
            "peak": 0,
            "dataPoints": 0
        }
        self.c.Open()
        self.CPU = self.c.Hardware[0].Name
        self.GPU = self.c.Hardware[1].Name
        self.c.Close()

    def getCPUMetrics(self):
        # Return CPU Core and Temperature with sensor.
        # Return:
        #   data = {core_name -> str: temperature -> int}
        # CPU metrics can only be gathered in Admin mode
        self.c.Open()
        data = []
        cpu = self.c.Hardware[0]
        cpuSensor = self.c.Hardware[0].Sensors
        cpu.Update()
        for sensor in cpuSensor:
            if "Temperature" in str(sensor.SensorType):
                data.append({
                    'name':sensor.Name,
                    'value':sensor.Value
                })
                # print('temp:', sensor.Name, ":", sensor.Value)
        self.c.Close()

        return data

    def getGPUMetrics(self):
        # Return GPU Core and Temperature with sensor.
        # Return:
        #   data = {core_name -> str: temperature -> int}
        self.c.Open()
        data = []
        gpu = self.c.Hardware[1]
        gpuSensor = self.c.Hardware[1].Sensors
        gpu.Update()

        for sensor in gpuSensor:
            if "Temperature" in str(sensor.SensorType):
                data.append({
                    'name':sensor.Name,
                    'value':sensor.Value
                })
                # print('temp:', sensor.Name, ":", sensor.Value)
        self.c.Close()

        return data

    def fetch(self):
        # Fetch all relevant metrics and return in tuple
        # Return
        #   (metrics...)        
        CPUInfo = self.getCPUMetrics()
        GPUInfo = self.getGPUMetrics()

        return CPUInfo, GPUInfo
    
    def registerData(self):
        # Register temperatures to be read from Graph in self.dataPoints
        cpuTempUpdate, gpuTempUpdate = self.fetch()
        # Register core names in dataPoints if they dont exist and append data
        toUpdate = cpuTempUpdate + gpuTempUpdate
        for updates in toUpdate:
            core = updates['name']
            if core in self.dataPoints:
                self.dataPoints[core].append(updates['value'])
                # update average and peak
            else:
                self.dataPoints[core] = [updates['value']]
            self.statistics['average'] += updates['value']
            if self.statistics['peak'] < updates['value']: self.statistics['peak'] = updates['value']
            self.statistics['dataPoints'] += 1


    def buildGraph(self, n_intervals):
        self.registerData()
        fig = make_subplots(rows=2, cols=2, subplot_titles=list(self.dataPoints.keys()))
        row_col_map = [(1, 1), (1, 2), (2, 1), (2, 2)]
        for i, (key, value) in enumerate(self.dataPoints.items()):
            row, col = row_col_map[i]

            fig.add_trace(
                go.Line(x=pd.Series(range(len(value))), y=value, name=key),
                row=row, col=col
            )
            fig.update_xaxes(title_text="Time (s)", row=row, col=col)
            fig.update_yaxes(title_text="Temperature (°C)", row=row, col=col)

        # Update layout
        fig.update_layout(
            height=600,
            width=1000,
            title_text="Temperature Readings by Component"
        )

        fig.update_layout(
            font=dict(family="Courier New", size=12, color='whitesmoke'),
            paper_bgcolor = '#202020'
        )

        return fig
    
    def getStats(self, n_intervals):
        return html.P(f"Average: {self.statistics['average'] // self.statistics['dataPoints']}°C, Peak:{self.statistics['peak']}°C")

    def run(self):
        # Run Dash App and update data in real time
        # build real time app
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.H1(children='HHW Viewer', style={'textAlign':'center'}),
            html.H2(children='Heatwave Hardware Viewer', style={'textAlign':'center'}),
            html.P(children='Analyze CPU and GPU temperatures in Real Time', style={'textAlign':'center'}),

            html.Div(
                children=[
                    html.P(f"CPU: {self.CPU}"),
                    html.P(f"GPU: {self.GPU}"),
                ],
                className="statBox"
            ),

            # plotly starts here
            html.Div(
                children=dcc.Graph(id='live-update-graph'),
                className="graphBox"
            ),

            html.Div(
                children=[
                    html.P("Statistics"),
                    html.Div(
                        id="live-update-stats"
                    )
                ],
                className="statBox",
                id="stats-screen"
            ),
            
            dcc.Interval(
                id='interval-component',
                interval= self.frequency * 1000, # convert s->ms
                n_intervals=0
            )
        ])
        #figure.show(renderer='browser')
        
        app.callback(
            Output('live-update-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )(self.buildGraph)

        app.callback(
            Output('live-update-stats', 'children'),
            Input('interval-component', 'n_intervals')
        )(self.getStats)
        

        app.run(debug=True)
