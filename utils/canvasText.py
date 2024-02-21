import Global


class TextCanvas:
    def __init__(self, parent):
        self.root = parent
        self.text_canvas = self.root.text_canvas
        self.source_text = None
        self.result_text = None

    def draw_text(self, source, result,extra=None):
        source_height = None
        if extra is not None:
            source = extra
            result = extra
        if self.source_text:
            self.text_canvas.delete(self.source_text)
        if self.result_text:
            self.text_canvas.delete(self.result_text)
        if not Global.sourceHide:
            self.source_text = self.text_canvas.create_text(10, 10, text=source, font=(
                self.root.source_fontName, self.root.source_fontSize, self.root.source_fontWeight),
                                                            fill=self.root.source_fontColor, anchor="nw",
                                                            justify="left", width=680)
            source_bbox = self.text_canvas.bbox(self.source_text)
            source_height = source_bbox[3] - source_bbox[1]  # 计算原文的高度
        y = source_height + 10 if source_height else 10
        self.result_text = self.text_canvas.create_text(10, y, text=result, font=(self.root.result_fontName,
                                                                                  self.root.result_fontSize,
                                                                                  self.root.result_fontWeight),
                                                        fill=self.root.result_fontColor, anchor="nw",
                                                        justify="left", width=680)
        result_bbox = self.text_canvas.bbox(self.result_text)
        canvas_height = result_bbox[3] + 10
        self.text_canvas.config(height=canvas_height)
