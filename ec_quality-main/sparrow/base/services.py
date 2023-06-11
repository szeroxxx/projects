from sparrow.dbengine import DBEngineSql
from sqlalchemy.sql import text


class ReleaseNoteOperation:
    def get_latest_release_version():
        # with DBEngineSql().connect() as conn:
        #     release_notes = conn.execute(text("select * from ReleaseNotes order by -id")).first()
        #     latest_version = release_notes["version"] if release_notes is not None else None
        return 1

    def get_release_note_details(old_version):
        release_details = {}
        release_note_version = ReleaseNoteOperation.get_latest_release_version()
        release_details["release_note_version"] = release_note_version
        if release_note_version != old_version:
            # with DBEngineSql().connect() as conn:
            #     latest_count = conn.execute(text(f"select count(*) from ReleaseNotes where version BETWEEN '{old_version}' AND '{release_note_version}' ;")).first()
            #     if (latest_count[0] - 1) > 0:
            #         count = latest_count[0] - 1
            #     else:
            #         count = 1
            release_details["release_note_count"] = 1
        else:
            release_details["release_note_count"] = 0

        return release_details
