def update_name(name, email):
    return "Filipe Ramos", "2978-Filipe.Ramos@users.noreply.gitlab.unige.ch"

def update_committer(name, email):
    return "Filipe Ramos", "2978-Filipe.Ramos@users.noreply.gitlab.unige.ch"

# Lancer git filter-repo avec ce script
if __name__ == "__main__":
    import git_filter_repo as gr

    gr.FilterRepo(
        options=gr.Options(name_callback=update_name, committer_callback=update_committer)
    ).run()

