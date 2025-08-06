from pydriller import Repository

out_file = open("sage_commits_2.txt", "w")
repo_url = 'sage/'

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
