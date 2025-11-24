def is_sentence_end(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    end_chars = ("。", "、", "！", "？", ".", "!", "?")
    closing_brackets = ("」", "』", "）", ")", "】", "]", '"', "'")
    last_char = ""
    for char_val in reversed(text):
        if not char_val.isspace():
            last_char = char_val
            break
    if not last_char:
        return False
    if last_char in end_chars:
        return True
    if last_char in closing_brackets:
        if len(text) > 1:
            temp_text = text
            while temp_text.endswith(last_char) or temp_text.endswith(" "):
                if temp_text.endswith(last_char):
                    temp_text = temp_text[: -len(last_char)]
                else:
                    temp_text = temp_text[:-1]
            second_last_char = ""
            if temp_text:
                for char_val_inner in reversed(temp_text):
                    if not char_val_inner.isspace():
                        second_last_char = char_val_inner
                        break
                if second_last_char in end_chars:
                    return True
    return False


def check_horizontal_proximity(
    box1_data,
    box2_data,
    max_vertical_diff_ratio=0.6,
    max_horizontal_gap_ratio=1.5,
    min_overlap_ratio=-0.2,
):
    if "bbox" not in box1_data or "bbox" not in box2_data:
        return False
    box1 = box1_data["bbox"]
    box2 = box2_data["bbox"]
    if not (box1 and box2 and len(box1) == 4 and len(box2) == 4):
        return False
    b1_x0, b1_y0, b1_x1, b1_y1 = box1
    b2_x0, b2_y0, b2_x1, b2_y1 = box2
    if b1_x0 > b2_x0 and b1_x1 > b2_x1 and b1_x0 > b2_x1:
        return False
    h1 = b1_y1 - b1_y0
    h2 = b2_y1 - b2_y0
    if h1 <= 0 or h2 <= 0:
        return False
    center1_y = (b1_y0 + b1_y1) / 2
    center2_y = (b2_y0 + b2_y1) / 2
    avg_h = (h1 + h2) / 2
    if avg_h <= 0:
        return False
    vertical_diff = abs(center1_y - center2_y)
    if vertical_diff > avg_h * max_vertical_diff_ratio:
        return False
    if b1_x1 <= b2_x0:
        horizontal_gap = b2_x0 - b1_x1
        if horizontal_gap > avg_h * max_horizontal_gap_ratio:
            return False
    else:
        if b2_x0 < b1_x0:
            overlap = min(b1_x1, b2_x1) - max(b1_x0, b2_x0)
            if overlap < avg_h * min_overlap_ratio:
                pass
        if b2_x0 < b1_x0 and (b1_x0 - b2_x0 > avg_h * 0.5):
            return False
    return True


def process_ocr_results_merge_lines(ocr_output_raw_segments: list, lang_hint="ja"):
    if not ocr_output_raw_segments or not isinstance(ocr_output_raw_segments, list):
        return []
    raw_blocks = []
    try:
        for i, item_data in enumerate(ocr_output_raw_segments):
            if not isinstance(item_data, (list, tuple)) or len(item_data) != 2:
                continue
            box_info_raw = item_data[0]
            text_info_raw = item_data[1]
            text_content_str = ""
            if (
                isinstance(text_info_raw, tuple)
                and len(text_info_raw) >= 1
                and isinstance(text_info_raw[0], str)
            ):
                text_content_str = text_info_raw[0].strip()
            elif (
                isinstance(text_info_raw, list)
                and len(text_info_raw) >= 1
                and isinstance(text_info_raw[0], str)
            ):
                text_content_str = text_info_raw[0].strip()
            elif isinstance(text_info_raw, str):
                text_content_str = text_info_raw.strip()
            else:
                continue
            if not text_content_str:
                continue
            vertices_parsed = []
            if isinstance(box_info_raw, list) and len(box_info_raw) == 4:
                valid_points = True
                for p_idx, p in enumerate(box_info_raw):
                    if isinstance(p, (list, tuple)) and len(p) == 2:
                        try:
                            vertices_parsed.append(
                                (int(round(float(p[0]))), int(round(float(p[1]))))
                            )
                        except (ValueError, TypeError):
                            valid_points = False
                            break
                    else:
                        valid_points = False
                        break
                if not valid_points:
                    vertices_parsed = []
            elif isinstance(box_info_raw, list) and len(box_info_raw) == 8:
                try:
                    temp_v = []
                    for k_coord in range(0, 8, 2):
                        temp_v.append(
                            (
                                int(round(float(box_info_raw[k_coord]))),
                                int(round(float(box_info_raw[k_coord + 1]))),
                            )
                        )
                    if len(temp_v) == 4:
                        vertices_parsed = temp_v
                    else:
                        vertices_parsed = []
                except (ValueError, TypeError):
                    vertices_parsed = []
            else:
                vertices_parsed = []
            if not vertices_parsed:
                continue
            x_coords_list = [v[0] for v in vertices_parsed]
            y_coords_list = [v[1] for v in vertices_parsed]
            bbox_rect = [
                min(x_coords_list),
                min(y_coords_list),
                max(x_coords_list),
                max(y_coords_list),
            ]
            if not (bbox_rect[2] > bbox_rect[0] and bbox_rect[3] > bbox_rect[1]):
                continue
            raw_blocks.append(
                {
                    "id": i,
                    "text": text_content_str,
                    "bbox": bbox_rect,
                    "vertices": vertices_parsed,
                }
            )
    except Exception as e:
        print(f"错误(process_ocr_results_merge_lines) - initial parsing: {e}")
        return []
    if not raw_blocks:
        return []
    raw_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
    merged_results = []
    processed_block_ids = set()
    for i in range(len(raw_blocks)):
        if raw_blocks[i]["id"] in processed_block_ids:
            continue
        current_block_data = raw_blocks[i]
        current_text_line = current_block_data["text"]
        current_line_vertices_representation = list(current_block_data["vertices"])
        current_line_bbox = list(current_block_data["bbox"])
        last_merged_block_in_this_line = current_block_data
        processed_block_ids.add(current_block_data["id"])
        for j in range(i + 1, len(raw_blocks)):
            next_block_candidate_data = raw_blocks[j]
            if next_block_candidate_data["id"] in processed_block_ids:
                continue
            should_merge_flag = False
            if not is_sentence_end(current_text_line):
                if check_horizontal_proximity(
                    last_merged_block_in_this_line, next_block_candidate_data
                ):
                    should_merge_flag = True
            if should_merge_flag:
                joiner = ""
                if lang_hint not in [
                    "ja",
                    "zh",
                    "ko",
                    "jpn",
                    "chi_sim",
                    "kor",
                    "chinese_sim",
                ]:
                    if current_text_line and next_block_candidate_data["text"]:
                        if not current_text_line.endswith(
                            ("-", "=", "#")
                        ) and not next_block_candidate_data["text"][0] in (
                            ".",
                            ",",
                            "!",
                            "?",
                            ":",
                            ";",
                        ):
                            joiner = " "
                current_text_line += joiner + next_block_candidate_data["text"]
                next_bbox = next_block_candidate_data["bbox"]
                current_line_bbox[0] = min(current_line_bbox[0], next_bbox[0])
                current_line_bbox[1] = min(current_line_bbox[1], next_bbox[1])
                current_line_bbox[2] = max(current_line_bbox[2], next_bbox[2])
                current_line_bbox[3] = max(current_line_bbox[3], next_bbox[3])
                last_merged_block_in_this_line = next_block_candidate_data
                processed_block_ids.add(next_block_candidate_data["id"])
            else:
                break
        merged_results.append((current_text_line, current_line_vertices_representation))
    return merged_results
