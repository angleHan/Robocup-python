
#!/usr/bin/env python
# -*- coding:utf-8 -*-

from construct import Byte, Struct, Enum, Bytes, Const, Array, Int16ub, Renamed
# from construct import *

Short = Int16ub

RobotInfo = "robot_info" / Struct(
    "penalty" / Enum(Byte,
                        PENALTY_NONE=0,
                        PENALTY_SPL_ILLEGAL_BALL_CONTACT=1,
                        PENALTY_SPL_PLAYER_PUSHING=2,
                        PENALTY_SPL_ILLEGAL_MOTION_IN_SET=3,
                        PENALTY_SPL_INACTIVE_PLAYER=4,
                        PENALTY_SPL_ILLEGAL_DEFENDER=5,
                        PENALTY_SPL_LEAVING_THE_FIELD=6,
                        PENALTY_SPL_KICK_OFF_GOAL=7,
                        PENALTY_SPL_REQUEST_FOR_PICKUP=8,
                        PENALTY_SPL_LOCAL_GAME_STUCK=9,
                        PENALTY_SUBSTITUTE=14,
                        PENALTY_MANUAL=15

    ),
    "secs_till_unpenalised" / Byte
)

TeamInfo = "team" / Struct(
    "team_number" / Byte,
    "team_color" / Enum(Byte,
                        BLUE=0,
                        RED=1,
                        YELLOW=2,
                        BLACK=3,
                        WHITE=4,
                        GREEN=5,
                        ORANGE=6,
                        PURPLE=7,
                        BROWN=8,
                        GRAY=9
                        ),
    "score" / Byte,
    "penalty_shot" / Byte,  # penalty shot counter
    "single_shots" / Short,  # bits represent penalty shot success
    "players" / Array(6, RobotInfo)
)

GameState = "gamedata" / Struct(
    "header" / Const(Bytes(4), b'RGme'),
    "version" / Const(Byte, 11),        # change "12" to "11"
    "packet_number" / Short,
    "players_per_team" / Byte,
    "competition_phase" / Enum(Byte,
                            COMPETITION_PHASE_ROUNDROBIN=0,
                            COMPETITION_PHASE_PLAYOFF=1
    ),   
    "competition_type" / Enum(Byte,   
                            COMPETITION_TYPE_NORMAL=0,
                            COMPETITION_TYPE_MIXEDTEAM=1,
                            COMPETITION_TYPE_GENERAL_PENALTY_KICK=2
    ),
    "game_phase" /Enum(Byte,
                            GAME_PHASE_NORMAL=0,
                            GAME_PHASE_PENALTYSHOOT=1,
                            GAME_PHASE_OVERTIME=2,
                            GAME_PHASE_TIMEOUT=3
    ),
    "game_state" / Enum(Byte,
                        STATE_INITIAL=0,
                        # Go to startposition
                        STATE_READY=1,
                        # be ready
                        STATE_SET=2,
                        # playing
                        STATE_PLAYING=3,
                        # game is end
                        STATE_FINISHED=4
                        ),
    "set_play" / Enum(Byte,
                    SET_PLAY_NONE=0,
                    SET_PLAY_GOAL_FREE_KICK=1,
                    SET_PLAY_PUSHING_FREE_KICK=2
                    ),
    "first_half" / Byte,
    "kicking_team" / Byte,
    "drop_in_team" / Byte,
    "drop_in_time" / Short,
    "secs_remaining" / Short,
    "secondary_time" / Short,
    Array(2, Renamed("teams", TeamInfo))
)

GAME_CONTROLLER_RESPONSE_VERSION = 7
GAMECONTROLLER_RETURN_STRUCT_VERSION = 3

ReturnData = "returndata" / Struct(
    "header" / Const(Bytes(4), b"RGrt"),
    "version" / Const(Byte, 3),         # change "2" to "3"
    "team" / Byte,
    "player" / Byte,
    "message" / Byte
)