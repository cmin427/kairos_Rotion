from robot_module.robotParts import AGV_PositionController

agv=AGV_PositionController()

agv.set_agv_mode_stop()

agv.set_agv_mode_direct_controll()

agv.agv_direct_controll("C_goahead_T_3")

agv.set_agv_mode_stop()



