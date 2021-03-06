from nwpc_workflow_log_model.log_record.log_record import LogRecord


def get_log_info_from_local_file(
        log_file: str,
        record_class: LogRecord,
):
    with open(log_file) as f:
        first_line = f.readline()
        if first_line is None:
            return {
                "file_path": log_file,
                "line_count": 0
            }
        first_record = record_class()
        first_record.parse(first_line)

        cur_line_no = 1
        cur_line = first_line
        for line in f:
            cur_line = line
            cur_line_no += 1
        last_record = record_class()
        last_record.parse(cur_line)
        return {
            "file_path": log_file,
            "line_count": cur_line_no,
            "range": {
                "start": {
                    "date": first_record.date.strftime("%Y-%m-%d"),
                    "time": first_record.time.strftime("%H:%M:%S"),
                },
                "end": {
                    "date": last_record.date.strftime("%Y-%m-%d"),
                    "time": last_record.time.strftime("%H:%M:%S"),
                },
            },
        }
