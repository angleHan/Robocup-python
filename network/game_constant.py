
class Penalty():
    PENALTY_NONE=0
    PENALTY_SPL_ILLEGAL_BALL_CONTACT=1
    PENALTY_SPL_PLAYER_PUSHING=2
    PENALTY_SPL_ILLEGAL_MOTION_IN_SET=3
    PENALTY_SPL_INACTIVE_PLAYER=4
    PENALTY_SPL_ILLEGAL_DEFENDER=5
    PENALTY_SPL_LEAVING_THE_FIELD=6
    PENALTY_SPL_KICK_OFF_GOAL=7
    PENALTY_SPL_REQUEST_FOR_PICKUP=8
    PENALTY_SPL_LOCAL_GAME_STUCK=9
    PENALTY_SUBSTITUTE=14
    PENALTY_MANUAL=15

class TeamColor():
    BLUE=0
    RED=1
    YELLOW=2
    BLACK=3
    WHITE=4
    GREEN=5
    ORANGE=6
    PURPLE=7
    BROWN=8
    GRAY=9

class CompetitionType():
    COMPETITION_TYPE_NORMAL=0
    COMPETITION_TYPE_MIXEDTEAM=1
    COMPETITION_TYPE_GENERAL_PENALTY_KICK=2

class CompetitionPhase():
    COMPETITION_PHASE_ROUNDROBIN=0
    COMPETITION_PHASE_PLAYOFF=1

class GamePhase():
    GAME_PHASE_NORMAL=0
    GAME_PHASE_PENALTYSHOOT=1
    GAME_PHASE_OVERTIME=2
    GAME_PHASE_TIMEOUT=3

class GameStateInfo():
    STATE_INITIAL=0,
    # Go to startposition
    STATE_READY=1
    # be ready
    STATE_SET=2
    # playing
    STATE_PLAYING=3
    # game is end
    STATE_FINISHED=4,

    PLAYERS_PER_TEAM=6

class SetPlay():
    SET_PLAY_NONE=0
    SET_PLAY_GOAL_FREE_KICK=1
    SET_PLAY_PUSHING_FREE_KICK=2
