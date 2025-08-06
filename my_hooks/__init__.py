def my_pre_init_hook(env):
    print("inside pre init hook")
    print(env['department.department'].search([]))
    for department in env['department.department'].search([]):
        print(department.name)

def my_post_init_hook(env):
    print("I am post Init Hook")

def my_uninstall_hook(env):
    print("I am uninstall hook")

def my_post_load_hook(env):
    print("I am Post load Hook")