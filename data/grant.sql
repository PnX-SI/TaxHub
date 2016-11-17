ALTER SCHEMA utilisateurs OWNER TO $usershub_user;
ALTER FOREIGN TABLE utilisateurs.t_applications OWNER TO $usershub_user;
ALTER FOREIGN TABLE utilisateurs.t_roles OWNER TO $usershub_user;
ALTER FOREIGN TABLE utilisateurs.v_userslist_forall_applications OWNER TO $usershub_user;
ALTER FOREIGN TABLE utilisateurs.v_userslist_forall_menu OWNER TO $usershub_user;