import datetime

from loguru import logger
from nwpc_workflow_log_model.rmdb.sms.record import SmsRecord
from nwpc_workflow_log_model.rmdb.util.session import get_session
from nwpc_workflow_log_model.rmdb.util.version_util import VersionUtil

from .log_file_util import (
    is_record_line,
    get_line_no_range,
)


def collect_log_from_local_file(
    config: dict, owner_name: str, repo_name: str, file_path: str, verbose
):
    session = get_session(config["collector"]["rdbms"]["database_uri"])

    with open(file_path) as f:
        first_line = f.readline().strip()
        version = VersionUtil.get_version(
            session, owner_name, repo_name, file_path, first_line, SmsRecord
        )
        SmsRecord.prepare(owner_name, repo_name)

        query = (
            session.query(SmsRecord)
            .filter(SmsRecord.repo_id == version.repo_id)
            .filter(SmsRecord.version_id == version.version_id)
            .order_by(SmsRecord.line_no.desc())
            .limit(1)
        )

        latest_record = query.first()
        if latest_record is None:
            start_line_no = 0
        else:
            start_line_no = latest_record.line_no + 1

        if start_line_no == 0:
            record = SmsRecord()
            record.parse(first_line)
            record.repo_id = version.repo_id
            record.version_id = version.version_id
            record.line_no = 0
            session.add(record)
            start_line_no += 1

        for i in range(1, start_line_no):
            f.readline()

        session_count_to_be_committed = 0

        cur_line_no = start_line_no
        commit_begin_line_no = cur_line_no
        for line in f:
            line = line.strip()
            if not is_record_line(line):
                cur_line_no += 1
                continue
            record = SmsRecord()
            if verbose > 1:
                print(cur_line_no, line)
            record.parse(line)
            record.repo_id = version.repo_id
            record.version_id = version.version_id
            record.line_no = cur_line_no
            session.add(record)
            cur_line_no += 1

            session_count_to_be_committed += 1
            if (
                session_count_to_be_committed
                >= config["collector"]["post"]["max_count"]
            ):
                commit_end_line_no = cur_line_no
                session.commit()
                logger.info(
                    "[{time}] commit session, line range: [{begin_line_no}, {end_line_no}]".format(
                        time=datetime.datetime.now(),
                        begin_line_no=commit_begin_line_no,
                        end_line_no=commit_end_line_no,
                    )
                )
                session_count_to_be_committed = 0
                commit_begin_line_no = cur_line_no + 1

        if session_count_to_be_committed > 0:
            session.commit()
            logger.info("commit session, last lines.")


def collect_log_from_local_file_by_range(
    config: dict,
    owner_name: str,
    repo_name: str,
    file_path: str,
    start_date,
    stop_date,
    verbose,
):
    session = get_session(config["collector"]["rdbms"]["database_uri"])

    with open(file_path) as f:
        first_line = f.readline().strip()
        version = VersionUtil.get_version(
            session, owner_name, repo_name, file_path, first_line, SmsRecord
        )
        SmsRecord.prepare(owner_name, repo_name)

        print("Finding line no in range:", start_date, stop_date)
        begin_line_no, end_line_no = get_line_no_range(
            file_path,
            datetime.datetime.strptime(start_date, "%Y-%m-%d").date(),
            datetime.datetime.strptime(stop_date, "%Y-%m-%d").date(),
        )
        if begin_line_no == 0 or end_line_no == 0:
            logger.info("line not found")
            return
        print("Found line no in range:", begin_line_no, end_line_no)

        for i in range(1, begin_line_no):
            f.readline()

        session_count_to_be_committed = 0
        max_count = config["collector"]["post"]["max_count"]
        # max_count = 1

        cur_line_no = begin_line_no
        commit_begin_line_no = cur_line_no
        for i in range(begin_line_no, end_line_no):
            line = f.readline()
            line = line.strip()
            if not is_record_line(line):
                cur_line_no += 1
                continue
            record = SmsRecord()
            if verbose > 1:
                print(cur_line_no, line)
            record.parse(line)
            record.repo_id = version.repo_id
            record.version_id = version.version_id
            record.line_no = cur_line_no
            record = session.add(record)
            cur_line_no += 1

            session_count_to_be_committed += 1
            if session_count_to_be_committed >= max_count:
                commit_end_line_no = cur_line_no
                session.commit()
                logger.info(
                    "[{time}] commit session, line range: [{begin_line_no}, {end_line_no}]".format(
                        time=datetime.datetime.now(),
                        begin_line_no=commit_begin_line_no,
                        end_line_no=commit_end_line_no,
                    )
                )
                session_count_to_be_committed = 0
                commit_begin_line_no = cur_line_no + 1

        if session_count_to_be_committed > 0:
            session.commit()
            logger.info("commit session, last lines.")