from browser import window, document

from vue import VueComponent, computed


class Grid(VueComponent):
    margin: int = 5

    col_num = 0
    item_size = 1
    template = """
        <grid-layout
            id="grid"
            :layout="layout"
            :col-num="col_num"
            :row-height="item_size"
            :vertical-compact="false"
            :margin="[margin, margin]"
            :use-css-transforms="true"
            style="background-color: white; height: 100%;"
            @layout-updated="layout_update"
        >
            <grid-item
                v-for="item in items" 
                :key="item.layout.i"
                v-bind="item.layout"
            >
                <component
                    :is="item.type"
                    :widget_id="item.layout.i"
                >
                </component>
            </grid-item>
        </grid-layout>
    """

    @computed
    def layout(self):
        return [
            w["layout"] for w in self.store.widgets
        ]

    @computed
    def items(self):
        return [item for item in self.store.widgets]

    def layout_update(self, layout):
        self.store.commit("set_layout", layout)

    def resize(self, ev):
        width = document["grid"].getBoundingClientRect().width
        self.col_num = int(width / (self.item_size + self.margin))

    def mounted(self):
        window.bind("resize", self.resize)
        self.resize(None)


Grid.register()
