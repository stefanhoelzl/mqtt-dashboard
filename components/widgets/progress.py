from .widget import Widget


class Progress(Widget):
    template_slots = """
    <el-progress 
        type="circle" 
        :percentage="int_value">
    </el-progress>
    """


Progress.register("mdb-progress")
