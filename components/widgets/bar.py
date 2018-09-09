from .widget import Widget


class Bar(Widget):
    template_slots = """
    <el-slider 
        :min="0"
        :max="40"
        show-input
        :show-input-controls="false"
        :value="int_value"
        disabled>
    </el-slider>
    """


Bar.register("mdb-bar")
