CREATE TABLE IF NOT EXISTS recommend_influencer (
            influencer_name TEXT, -- SocialUser
            bio TEXT, /*LIST < list of characteristics >  not see */
            categories list<text>, /*LIST < list of business catagory >, hashtag, keyword*/
            commentPerPost int,
            demographics TEXT, --age, gender, 
            engagementRate TEXT,
            follower int,
            account_type int, -- 0: influencer, 1: branch, 2: all
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
            PRIMARY KEY (influencer_id, ts)
        ) WITH CLUSTERING ORDER BY (ts DESC) ;



user aify_recommend;
CREATE TABLE IF NOT EXISTS aify_recommend.user_business_discovery (
    id bigint,
    name text,
    biography text,
    media_count int,
    comments_count int,     
    likes_count int,
    followers_count int,
    username text,
    profile_picture_url text,
    ts timeuuid,
    PRIMARY KEY (id, ts)
) WITH CLUSTERING ORDER BY (ts DESC);


CREATE TABLE IF NOT EXISTS aify_recommend.Person (
    id timeuuid,
    first_name text,
    last_name text,
    PRIMARY KEY(id)
) WITH CLUSTERING ORDER BY (id DESC);