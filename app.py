from browser.local_storage import storage
from browser.object_storage import ObjectStorage

from vue import VueComponent, Vue, VueStore, getter, mutation, VueStorePlugin
from vue.bridge import Object
from components import *

from vue.utils import js_lib

VueMqtt = js_lib("VueMqtt")
Vue.use(VueMqtt, 'mqtts://test.mosquitto.org:8081')

VueGridLayout = js_lib("VueGridLayout")
Vue.component("grid-layout", VueGridLayout.GridLayout)
Vue.component("grid-item", VueGridLayout.GridItem)

default_widgets = [
    {"type": "mdb-progress",
     "props": {"topic": "vuepy/loading"},
     "layout": {"x": 50, "y": 10, "w": 22, "h": 22, "isResizable": False}},

    {"type": "mdb-bar",
     "props": {"topic": "vuepy/temperature"},
     "layout": {"x": 0, "y": 0, "w": 70, "h": 8, "minH": 8, "maxH": 8}},

    {"type": "mdb-button",
     "props": {"topic": "vuepy/window"},
     "layout": {"x": 150, "y": 10, "w": 16, "h": 8, "isResizable": False}},

    {"type": "mdb-generator",
     "props": {
         "profiles": [
             {"topic": "vuepy/loading",
              "settings": {"name": "saw", "min": 0, "max": 100},
              "enabled": True, "frequency": 100},
             {"topic": "vuepy/temperature",
              "settings": {"name": "rand", "init": 25, "var": 1},
              "enabled": True, "frequency": 1000},
         ]
     },
     "layout": {"x": 100, "y": 20, "w": 100, "h": 26, "isResizable": False}},
]

object_storage = ObjectStorage(storage)
if True or "widgets" not in object_storage:
    object_storage["widgets"] = default_widgets


class StoragePlugin(VueStorePlugin):
    def initialize(self, store):
        for widget in object_storage["widgets"]:
            store.commit("add_widget", widget)

    def subscribe(self, state, *args, **kwargs):
        object_storage["widgets"] = Object.to_py(state.widgets)


class Store(VueStore):
    widgets = []
    next_widget_id = 0

    plugins = [StoragePlugin().install]

    @getter
    def props(self, widget_id):
        return self.widgets[int(widget_id)]["props"]

    @mutation
    def set_props(self, widget_id, props):
        self.widgets[int(widget_id)]["props"] = props

    @mutation
    def set_layout(self, complete_layout):
        for idx, layout in enumerate(complete_layout):
            self.widgets[idx]["layout"] = layout

    @mutation
    def add_widget(self, widget):
        widget["layout"]["i"] = str(self.next_widget_id)
        self.widgets.append(widget)
        self.next_widget_id += 1

    @mutation
    def set_height(self, widget_id, height):
        self.widgets[int(widget_id)]['layout']['h'] = height


class App(VueComponent):
    loading = 0
    temperature = 22

    template = """
    <el-container>
        <el-main>
            <grid></grid>
        </el-main>
    </el-container>
    """


app = App("#app", store=Store())
