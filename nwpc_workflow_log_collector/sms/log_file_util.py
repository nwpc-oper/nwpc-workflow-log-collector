import datetime
from itertools import islice


def get_date_from_line(line):
    start_pos = 7
    end_pos = line.find("]", start_pos)
    time_string = line[start_pos:end_pos]
    date_time = datetime.datetime.strptime(time_string, "%H:%M:%S %d.%m.%Y")
    line_date = date_time.date()
    return line_date


def is_record_line(log_line: str):
    return log_line.startswith("#")


def get_line_no_range(
    log_file_path: str,
    begin_date: datetime.date,
    end_date: datetime.date,
    max_line_no: int = 1000,
):
    begin_line_no = 0
    end_line_no = 0
    with open(log_file_path) as log_file:
        cur_first_line_no = 1
        while True:
            next_n_lines = list(islice(log_file, max_line_no))
            if not next_n_lines:
                return begin_line_no, end_line_no

            # if last line less then begin date, skip to next turn.
            cur_pos = -1
            cur_last_line = next_n_lines[-1]
            while (-1 * cur_pos) < len(next_n_lines):
                cur_last_line = next_n_lines[cur_pos]
                if is_record_line(cur_last_line):
                    break
                cur_pos -= 1

            line_date = get_date_from_line(cur_last_line)
            if line_date < begin_date:
                cur_first_line_no = cur_first_line_no + len(next_n_lines)
                continue

            # find first line greater or equal to start_date
            for i in range(0, len(next_n_lines)):
                cur_line = next_n_lines[i]
                if not is_record_line(cur_line):
                    continue
                line_date = get_date_from_line(cur_line)
                if line_date >= begin_date:
                    begin_line_no = cur_first_line_no + i
                    break

            # begin line must be found
            assert begin_line_no > 0

            # check if some line greater or equal to stop_date,
            # if begin_line_no == end_line_no, then there is no line returned.
            for i in range(begin_line_no - 1, len(next_n_lines)):
                cur_line = next_n_lines[i]
                if not is_record_line(cur_line):
                    continue
                line_date = get_date_from_line(cur_line)
                if line_date >= end_date:
                    end_line_no = cur_first_line_no + i
                    if begin_line_no == end_line_no:
                        begin_line_no = 0
                        end_line_no = 0
                    return begin_line_no, end_line_no
            cur_first_line_no = cur_first_line_no + len(next_n_lines)
            end_line_no = cur_first_line_no
            break

        while True:
            next_n_lines = list(islice(log_file, max_line_no))
            if not next_n_lines:
                break

            cur_last_line = next_n_lines[-1]
            cur_pos = -1
            while (-1 * cur_pos) < len(next_n_lines):
                cur_last_line = next_n_lines[cur_pos]
                if is_record_line(cur_last_line):
                    break
                cur_pos -= 1

            # if last line less than stop_date, skip to next run
            line_date = get_date_from_line(cur_last_line)
            if line_date < end_date:
                cur_first_line_no = cur_first_line_no + len(next_n_lines)
                continue

            # find stop_date
            for i in range(0, len(next_n_lines)):
                cur_line = next_n_lines[i]
                if not is_record_line(cur_line):
                    continue
                line_date = get_date_from_line(cur_line)
                if line_date >= end_date:
                    end_line_no = cur_first_line_no + i
                    return begin_line_no, end_line_no
            else:
                return begin_line_no, cur_first_line_no + len(next_n_lines)

    return begin_line_no, end_line_no
