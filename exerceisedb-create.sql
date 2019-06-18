create table if not exists exercise(
    id integer primary key ,
    name varchar unique,
    type varchar,
    group_name varchar,
    videourl varchar,
    gifurl varchar
);

create TABLE if not exists classifications(
    id integer primary key,
    utility varchar ,
    mechanics varchar,
    force varchar,
    function varchar,
    intensity varchar,
    unique (utility,mechanics,force,function,intensity)
);

create table if not exists exercise_classifications(
    classification_id integer,
    exercise_id integer,
    foreign key (classification_id) references classifications(id),
    foreign key (exercise_id) references exercise(id),
    primary key (classification_id,exercise_id)
);

create table if not exists instructions(
    id integer primary key,
    preparation varchar,
    execution varchar,
    easier varchar,
    comments varchar
);

create table if not exists exercise_instructions(
   instructions_id integer,
   exercise_id integer,
   foreign key (instructions_id) references instructions(id),
   foreign key (exercise_id) references exercise(id),
   primary key (instructions_id,exercise_id)
);

create TABLE if not exists muscles(
    id integer primary key,
    name varchar unique,
    link varchar
);

create table if not exists exercise_muscles(
    id integer primary key,
    muscles_type varchar, --dynamic, harder, static
    muscle_Id integer,
    exercise_id integer,
    foreign key (muscle_Id) references muscles(id),
    foreign key (exercise_id) references exercise(id)
);