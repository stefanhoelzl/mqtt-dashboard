from vue import computed
from .widget import Widget


class Button(Widget):
    states = {
        "open": {"type": "success", "text": "OPEN", "publish": "closed"},
        "closed": {"type": "primary", "text": "CLOSED", "publish": "open"},
    }
    default_state = states["open"]

    template_slots = """
    <el-button 
        :type="current_state.type" 
        @click="click" 
        round>
        {{ current_state.text }}
    </el-button>
    """

    @computed
    def current_state(self,):
        return self.states.get(self.value, self.default_state)

    def click(self, ev):
        self.value = self.current_state["publish"]


Button.register("mdb-button")
