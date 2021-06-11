user aify_db;
CREATE TABLE recommend_influencer (
            influencer_name TEXT, -- SocialUser
            bio TEXT, /*LIST < list of characteristics >  not see */
            categories list<text>, /*LIST < list of business catagory >, hashtag, keyword*/
            commentPerPost int,
            demographics TEXT, --age, gender, 
            engagementRate TEXT,
            follower int,
            account_type int, -- 0: influencer, 1: branch, 2: all
            instagram_id text,
            likePerPost int, --everage
            location TEXT,
            path TEXT,
            reach TEXT,
            website TEXT,
            posts_starting BIGINT,
            currency TEXT,
            socialAccounts list<frozen <map<text, text>>>,
            created TIMESTAMP,
            updated TIMESTAMP,
            activate TIMESTAMP,
            influencer_id INT,
            img_url TEXT,
            ts timeuuid,
            PRIMARY KEY (instagram_id)
        );


CREATE TABLE users_business_discovery (
    id bigint,
    name text,
    biography text,
    media_count int,
    comments_count int,     
    likes_count int,
    followers_count int,
    username text,
    profile_picture_url text,
    --ts timeuuid,
    updated_date TIMESTAMP,
    PRIMARY KEY (id, username)
) WITH CLUSTERING ORDER BY (username DESC);


--user definded type
CREATE TYPE type_business_info (
    id text,
    website text,
    media_count int,
    followers_count int,
    name text,
    username text,
    profile_picture_url text,
    new_post int,
    acc_type int
);
---alter type type_business_info add acc_type int

 --find how many new post
CREATE TABLE IF NOT EXISTS watch_list (
    user_id text, -- aify_id or instagram_id
    --watch_user_list list<frozen<map<text, int>>>, --map<username, current_post> (list of dict in python)
    watch_user_list map<text, frozen<type_business_info>>,
    viewed_time TIMESTAMP,
    updated_time timestamp,
    PRIMARY KEY(user_id)
) ;

CREATE TABLE IF NOT EXISTS recommend_result (
    num_count int,
    results map<text, text>,
    created TIMESTAMP,
    updated TIMESTAMP,
    owner_id UUID,
    PRIMARY KEY (owner_id)
);


-- test some operation
CREATE TABLE IF NOT EXISTS test.Person (
    id timeuuid,
    user_name text,
    first_name text,
    last_name text,
    PRIMARY KEY(id)
) WITH CLUSTERING ORDER BY (id DESC);