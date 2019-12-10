import sys
import json
import os
from graphviz import Digraph
from exp_parser import ExpressionParser
import xlsxwriter


parser = ExpressionParser()


def evaluateExpression(exp, context):
    if not isinstance(exp, str):
        return exp
    return parser.eval(exp, context["parameters"])


def getNodeName(node, context):
    name = ""
    if "type" in node:
        if node["type"] == "decision":
            name = "D{0}".format(context["counter"])
        elif node["type"] == "event":
            name = "E{0}".format(context["counter"])
    else:
        name = "L{0}".format(context["counter"])
    context["counter"] = context["counter"] + 1
    return name


def processDecisionNode(node, context):
    rv = node.copy()
    rv["name"] = getNodeName(node, context)

    alternatives = [processNode(n, context) for n in node["alternatives"]]
    if len(alternatives) == 0:
        rv["value"] = 0
        rv["alternatives"] = []
    else:        
        rv["value"] = max([n.get("value", 0) for n in alternatives])
        rv["alternatives"] = alternatives

    dot = context["dot"]
    dot.node(rv["name"], shape="square", fixedsize="true", xlabel="{:,.0f}".format(rv["value"]))
    for n in alternatives:
        penwidth = "1.0"
        if n["value"] == rv["value"]:
            penwidth = "3.0"
        dot.edge(rv["name"], n["name"], label=n["label"], arrowhead="none", penwidth=penwidth)

    # add formula for this node to the spreadsheet
    cells = ",".join([a["cell"] for a in alternatives])
    excel = context["excel"]
    row = excel["row"]
    worksheet = excel["worksheet"]
    worksheet.write(row-1, 0, rv["name"])
    worksheet.write(row-1, 1, "=MAX(" + cells + ")")
    if "label" in rv:
        worksheet.write(row-1, 2, rv["label"])
    rv["cell"] = "B" + str(row)
    excel["row"] = row + 1

    return rv


def processEventNode(node, context):
    rv = node.copy()
    rv["name"] = getNodeName(node, context)

    outcomes = [processNode(n, context) for n in node["outcomes"]]
    rv["value"] = sum([a.get("value",0)*evaluateExpression(a.get("probability", 0), context) for a in outcomes])
    rv["outcomes"] = outcomes

    dot = context["dot"]
    dot.node(rv["name"], shape="circle", fixedsize="true", xlabel="{:,.0f}".format(rv["value"]))
    for n in outcomes:
        dot.edge(rv["name"], n["name"], label=n["label"] + "\np=" + "{:,.2f}".format(evaluateExpression(n.get("probability", 0), context) ), arrowhead="none")

    # create the excel formula
    formula = "+".join([outcomes[i]["cell"] + "*(" + str(node["outcomes"][i]["probability"]) + ")" for i in range(0, len(outcomes))])

    # add this formula to the excel sheet
    excel = context["excel"]
    row = excel["row"]
    worksheet = excel["worksheet"]
    worksheet.write(row-1, 0, rv["name"])
    worksheet.write(row-1, 1, "=" + formula)
    if "label" in rv:
        worksheet.write(row-1, 2, rv["label"])
    rv["cell"] = "B" + str(row)
    excel["row"] = row + 1

    return rv


def processLeafNode(node, context):
    rv = node.copy()
    rv["name"] = getNodeName(node, context)
    rv["value"] = evaluateExpression(node["value"], context)

    dot = context["dot"]
    dot.node(rv["name"], shape="point", xlabel="{:}\n{:,.0f}".format(rv["name"],rv["value"]))

    # add this value to the spreadsheet
    excel = context["excel"]
    row = excel["row"]
    worksheet = excel["worksheet"]
    worksheet.write(row-1, 0, rv["name"])
    worksheet.write(row-1, 1, "=" + str(node["value"]))
    if "label" in rv:
        worksheet.write(row-1, 2, rv["label"])
    rv["cell"] = "B" + str(row)
    excel["row"] = row + 1

    return rv


def processNode(node, context):
    if "type" in node:
        if node["type"] == "decision":
            return processDecisionNode(node, context)
        elif node["type"] == "event":
            return processEventNode(node, context)
    elif "value" in node:
        return processLeafNode(node, context)
    return {}


def main():

    if len(sys.argv) <= 1:
        print("Usage: python " + sys.argv[0] + " <json file>")
        return

    # open the json file
    with open(sys.argv[1]) as data_file:
        data = json.load(data_file)

    dot = Digraph(comment="The Decision Tree", format="png")
    dot.attr(nodesep="1.2", rankdir="LR")

    workbook = xlsxwriter.Workbook('out/tree.xlsx')
    worksheet = workbook.add_worksheet("Tree")
    excel = {"worksheet": worksheet, "row": 1}

    parameters = {}
    context = {"counter": 1, "dot": dot, "parameters": parameters, "excel": excel}

    # process values
    for v in data["parameters"]:
        if "name" in v and "value" in v:
            parameters[v["name"]] = v["value"]
            row = excel["row"]
            worksheet.write(row-1, 0, v["value"])
            worksheet.write(row-1, 1, v["description"])
            workbook.define_name(v["name"], "Tree!$A$" + str(row))
            excel["row"] = row + 1

    # process expressions
    for v in data["parameters"]:
        if "name" in v and "expression" in v:
            parameters[v["name"]] = evaluateExpression(v["expression"], context)
            row = excel["row"]
            worksheet.write(row-1, 0, "=" + v["expression"])
            worksheet.write(row-1, 1, v["description"])
            workbook.define_name(v["name"], "Tree!$A$" + str(row))
            excel["row"] = row + 1

    # add an empty line in the excel file
    excel["row"] = excel["row"] + 1

    out = json.dumps(processNode(data["tree"], context), indent=4, sort_keys=False, ensure_ascii=False)

    if not os.path.exists("out"):
        os.makedirs("out")

    with open('out/out.json', 'w') as outfile:
        print(out, file=outfile)

    dot.render('out/tree', view=True)
    workbook.close()


if __name__ == '__main__':
    main()
