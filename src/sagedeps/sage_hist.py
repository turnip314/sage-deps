from pydriller import Repository, ModificationType

from constants import *
import json

repo_url = SAGE_BASE

def dump_commit_history():
    with open(COMMIT_HISTORY, "w") as out_file:
        for i, commit in enumerate(Repository(
            repo_url,
            only_in_branch='develop',
            only_no_merge=True,
        ).traverse_commits()):
            #out_file.write(commit.hash)
            out_file.write(f"Commit number: {i}, Date: {commit.author_date}")
            out_file.write(f"{commit.msg[:100]} + \n")
            out_file.write(f"{commit.author.name} + \n")

            for mod in commit.modified_files:
                out_file.write(f"{mod.new_path or "Deleted"} \n")
                out_file.write(f"{mod.change_type.name}\n")
            
            out_file.write(f"{"-"*100}\n")
            out_file.write("\n")
        out_file.write("END")

def get_file_update_metadata():
    """
    data = {
        file: {
            "num_commits": int,
            "total_adds": int,
            "total_dels": int,
            "created": data
        }
    }
    """
    data = {}
    for _, commit in enumerate(Repository(
        repo_url,
        only_in_branch='develop',
        only_no_merge=True,
    ).traverse_commits()):
        for mod in commit.modified_files:
            if mod.change_type == ModificationType.DELETE and mod.old_path in data:
                data[mod.old_path]["date_deleted"] = commit.committer_date.strftime("%Y-%m-%d")
            elif mod.new_path != mod.old_path and mod.old_path in data:
                data[mod.new_path] = data.pop(
                    mod.old_path, {
                        "num_commits": 0,
                        "total_adds": 0,
                        "total_dels": 0,
                    }
                )
            elif mod.new_path in data:
                data[mod.new_path]["num_commits"] += 1
                data[mod.new_path]["total_adds"] += mod.added_lines
                data[mod.new_path]["total_dels"] += mod.deleted_lines
            elif mod.change_type != ModificationType.DELETE:
                data[mod.new_path] = {
                    "num_commits": 1,
                    "total_adds": mod.added_lines,
                    "total_dels": mod.deleted_lines,
                    "created": commit.committer_date.strftime("%Y-%m-%d")
                }

    with open(COMMIT_METADATA, "w") as out_file:
        out_file.write(json.dumps(data))

if __name__ == "__main__":
    get_file_update_metadata()
