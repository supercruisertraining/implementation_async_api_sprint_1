from state.state_manager import RedisStateProvider, State

state_adapter = State(state_provider=RedisStateProvider())
