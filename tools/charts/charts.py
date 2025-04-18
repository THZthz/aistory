from pyecharts import options as opts
from pyecharts.charts import Graph
import json

if __name__ == '__main__':
    with open('./les-miserables.json', 'r', encoding='utf-8') as f:
        graph_data = json.load(f)

    graph = (
        Graph(init_opts=opts.InitOpts(width="100%", height="900px"))  # 可以调整画布大小
        .add(
            series_name="Les Miserables",
            nodes=graph_data["nodes"],
            links=graph_data["links"],
            categories=graph_data["categories"],
            layout="none",  # 力引导布局可以用 "force"，这里用 "none"
            is_roam=True,  # 允许缩放和平移
            is_focusnode=True,  # 允许聚焦节点
            label_opts=opts.LabelOpts(
                is_show=True,
                position="right",
                formatter="{b}"
            ),
            linestyle_opts=opts.LineStyleOpts(
                color="source",  # 线条颜色跟随源节点
                curve=0.3  # 线条曲率
            ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(),  # 提示框

        )
    )

    graph.render("les_miserables_graph.html")
