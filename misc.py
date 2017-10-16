
def prompt_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
            "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '{}'".format(default))

    choice = input(question + prompt)
    if choice in valid:
        return valid[choice]
    else:
        print("Please respond with 'y' or 'n'.")
        return(prompt_yes_no(question, default=default))
