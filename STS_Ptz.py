import time
from onvif import ONVIFCamera
from pyModbusTCP.client import ModbusClient
import pyModbusTCP.utils as util

IP = "192.168.100.111"   # Dirección IP de la cámara
PORT = 80             # Puerto
USER = "Software"        # Usuario
PASS = "Stiport1234"  # Contraseña
WSDL_DIR =r'C:/Users/usercms/Desktop/Camera_PTZ/wsdl'

plc_type = 'AC500' # 'AC500' or 'AC800'
plc_address = '192.168.100.81'  #AC500 = 100.81 or AC800 = 100.83


positionrequest = None
ptz = None
active = False
ptz_configuration_options = None
media_profile = None

Pos1=False
Pos2=False
Pos3=False
Pos4=False


connection = ModbusClient(host=plc_address, auto_open=True, debug = False)
connection.open()

        
def do_move(ptz, request):
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.AbsoluteMove(request)

def setup_move():
    global ptz, ptz_configuration_options, media_profile, positionrequest
    mycam = ONVIFCamera(IP, PORT, USER, PASS,WSDL_DIR)
    
    media = mycam.create_media_service()
    ptz = mycam.create_ptz_service()

    media_profile = media.GetProfiles()[0]

    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request_configuration = ptz.create_type('GetConfiguration')
    request_configuration.PTZConfigurationToken  = media_profile.PTZConfiguration.token
    ptz_configuration = ptz.GetConfiguration(request_configuration)

    request_setconfiguration = ptz.create_type('SetConfiguration')
    request_setconfiguration.PTZConfiguration = ptz_configuration

    positionrequest = ptz.create_type('AbsoluteMove')
    positionrequest.ProfileToken = media_profile.token

    if positionrequest.Position is None:
        positionrequest.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        positionrequest.Position.PanTilt.space = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].URI
        positionrequest.Position.Zoom.space = ptz_configuration_options.Spaces.AbsoluteZoomPositionSpace[0].URI
    if positionrequest.Speed is None:
        positionrequest.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        positionrequest.Speed.PanTilt.space = ptz_configuration_options.Spaces.PanTiltSpeedSpace[0].URI

def mover_a_un_lugar(x, y, zoom):
    global positionrequest
    positionrequest.Position.PanTilt.x = x
    positionrequest.Position.PanTilt.y = y
    positionrequest.Position.Zoom.x = zoom
    positionrequest.Speed.PanTilt.x=1
    positionrequest.Speed.PanTilt.y=1
    positionrequest.Speed.Zoom.x=1
    do_move(ptz, positionrequest)

def Calle_uno():
    global Pos1,Pos2,Pos3,Pos4
    if Pos1==False:
        setup_move()
        time.sleep(2)
        mover_a_un_lugar(-0.04, 0.65, 0.07)# Valores Fijos y seteados 06/05/2024 PP&RG
        Pos1=True
        Pos2=False
        Pos3=False
        Pos4=False

def Calle_Dos():
    global Pos1,Pos2,Pos3,Pos4
    if Pos2==False:
        setup_move()
        time.sleep(2)
        mover_a_un_lugar(0.01, 0.65, 0.05)# Valores Fijos y seteados 06/05/2024 PP&RG
        Pos2=True
        Pos1=False
        Pos3=False
        Pos4=False

def Calle_Tres():
    global Pos1,Pos2,Pos3,Pos4
    if Pos3==False:
        setup_move()
        time.sleep(2)
        mover_a_un_lugar(0.08, 0.65, 0)# Valores Fijos y seteados 06/05/2024 PP&RG
        Pos3=True
        Pos1=False
        Pos2=False
        Pos4=False
    
def Calle_Cuatro():
    global Pos1,Pos2,Pos3,Pos4
    if Pos4 == False:
        setup_move()
        time.sleep(2)
        mover_a_un_lugar(0.16, 0.70, 0)# Valores Fijos y seteados 06/05/2024 PP&RG
        Pos4=True
        Pos1=False
        Pos2=False
        Pos3=False


while True:
    if plc_type == 'AC500':
        try:
            hoist = connection.read_input_registers(2,2)
            trolley = connection.read_input_registers(4,2)
            
            trolley_long = util.word_list_to_long(trolley)
            trolley_float = util.decode_ieee(trolley_long[0])

            hoist_long = util.word_list_to_long(hoist)
            hoist_float = util.decode_ieee(hoist_long[0])
            
            if hoist_float>=0 and hoist_float<=10:
                if trolley_float>=-5.89 and trolley_float<=-4:
                    Calle_uno()
                if trolley_float>=-10.73 and trolley_float<=-8.54:
                    Calle_Dos()
                if trolley_float>=-15 and trolley_float<=-13.28:
                    Calle_Tres()
                if trolley_float>=-19.99 and trolley_float<=-18:
                    Calle_Cuatro()
        except Exception as a:
            print(a)