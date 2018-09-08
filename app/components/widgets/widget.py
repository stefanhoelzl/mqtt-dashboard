from vue import VueComponent, watch, computed


def mqtt_match(flt, topic):
    for f, t in zip(flt.split("/"), topic.split("/")):
        if f == "#":
            return True
        if f != "+" and f != t:
            return False
    return len(flt) == len(topic)


class Widget(VueComponent):
    extends = True
    template_merging = True
    template_slots = {
        "settings": """
        Topic
        <el-input 
            placeholder="Topic" 
            v-model="topic"
        ></el-input>
        """
    }
    widget_id: str

    topic = ""
    received_message = ""
    settings_visible = False
    has_settings = True

    template = """
    <div>
        <div @contextmenu.prevent="settings_visible = true && has_settings">
            {}
        </div>
        <el-dialog 
            title="Settings" 
            :visible.sync="settings_visible" 
            append-to-body
        >
            {settings}
        </el-dialog>
    </div>
    """

    def subscribe(self):
        if self.topic:
            self.mqtt.subscribe(self.topic)

    def get_prop(self, item):
        from vue.bridge import Object
        props = Object.to_py(self.store.props(self.widget_id))
        return props.get(item, None)

    def set_prop(self, prop, value):
        props = self.store.props(self.widget_id)
        props[prop] = value
        self.store.commit("set_props", self.widget_id, props)

    def set_height(self, h):
        self.store.commit("set_height", self.widget_id, h)

    @computed
    def topic(self):
        return self.get_prop("topic")

    @topic.setter
    def topic(self, new_topic):
        self.set_prop("topic", new_topic)

    @computed
    def value(self):
        return self.received_message

    @value.setter
    def value(self, value):
        self.mqtt.publish(self.topic, value)

    @computed
    def int_value(self):
        try:
            return int(self.value)
        except ValueError:
            return 0

    @int_value.setter
    def int_value(self, value):
        self.value = str(value)

    @watch("topic")
    def topic_changed(self, new, old):
        self.subscribe()

    def created(self):
        self.subscribe()
        self.mqtt.on("message", self.on_message)

    def on_message(self, topic, message, packet):
        if mqtt_match(self.topic, topic):
            self.received_message = str(message)
