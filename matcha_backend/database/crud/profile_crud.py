import logging
from ..dbmanager import DBManager
from psycopg2 import sql

class Profile(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
    
    def get_profile_by_user_id(self, user_id):
        """Retrieve profile by user ID"""
        result = self.select('profiles', where="user_id = %s", where_params=(user_id,))
        return result[0] if result else None

    def create_profile(self, profile_data):
        """Create a new profile"""
        return self.insert('profiles', profile_data)
    
    def update_profile(self, user_id, profile_data):
        """Update profile information"""
        return self.update('profiles', profile_data, where='user_id = %s', where_params=(user_id,))
    
    def delete_profile(self, user_id):
        """Delete a profile by user ID"""
        return self.delete('profiles', where='user_id = %s', where_params=(user_id,))
    
    def get_all_profiles(self):
        """Retrieve all profiles"""
        return self.select('profiles')


    def get_tag_id(self, tag_name):
        try:
            result = self.select('tags', "tag_id", where='tag_name = %s', where_params=(tag_name,))
            return result[0] if result else None
        except Exception as e:
            raise Exception(e)


    def insert_tag(self, tag_name):
        try:
            self.insert('tags', {"tag_name": tag_name}, "nothing", ["tag_name"])
            return self.get_tag_id(tag_name)
        except Exception as e:
            raise Exception(e)
        # if result: # If the INSERT succeeded and returned an id
        #     return result
        # else: #! If there was a conflict, get the existing id (do i need it?)
        #     return ("Aleready exists")
            # select_query = "SELECT tag_id FROM tags WHERE tag_name = %s;"
            # return self.execute(select_query, (tag_name,))[0]['tag_id']


    def add_user_interests(self, user_id, tag_id):
        return self.insert(
                table='user_tags', 
                data={"user_id": user_id, "tag_id": tag_id},
                on_conflict="nothing",
                conflict_target=["user_id", "tag_id"]
            )
        
        
    def remove_user_interest(self, user_id, tag_id):
        return self.delete(
                table='user_tags',
                where='user_id = %s AND tag_id = %s',
                where_params=(user_id, tag_id)
            )

    # def get_user_interests(self, user_id):
    #     logger = logging.getLogger(__name__)
        
    #     result = self.select('user_tags', "tag_id", where="user_id = %s", where_params=(user_id,))

    #     tag_ids = [tag['tag_id'] for tag in result]
    #     if not tag_ids:
    #         return []

        
    #     name_results = self.select('tags', "tag_name", where="tag_id", in_params=(tag_ids,))
    #     logger.debug(f"👉👉👉👉{name_results}👈👈👈👈 ")
    #     # if name_results is None:
    #     #     return []
    #     name_tags = [tag['tag_name'] for tag in name_results]
        
    #     return name_tags
    
    def get_user_interests(self, user_id):
        logger = logging.getLogger(__name__)
    
        # 1) fetch tag ids from the join table (make sure this table name matches your schema)
        rows = self.select(
            'user_tags',             # <-- if your table is actually user_interests, change this
            columns="tag_id",
            where="user_id = %s",
            where_params=(user_id,)
        )
        tag_ids = [r['tag_id'] for r in rows] if rows else []
        if not tag_ids:
            return []
    
        # 2) fetch tag names using ANY(array)
        name_rows = self.select(
            'tags',
            columns='tag_name',
            where='tag_id = ANY(%s)',
            where_params=(tag_ids,)  # pass list as a single param
        )
    
        logger.debug("get_user_interests: tag_ids=%s names=%s", tag_ids, name_rows)
        return [r['tag_name'] for r in (name_rows or [])]

    def insert_images(self, image_path, user_id):
        try:
            self.insert("images", {"user_id" : user_id,
                                    "image_url": image_path})
                        # on_conflict="nothing")
        except Exception as e:
            raise Exception(e)
    
    def get_images(self, user_id):
        logger = logging.getLogger(__name__)
        
        result = self.select('images', "image_url", where="user_id = %s", where_params=(user_id,))
        return [image['image_url'] for image in result]
    
    
    def delete_image(self, user_id, image_id):
        return self.delete(
            table='images',
            where="user_id = %s AND image_id = %s",
            where_params=(user_id, image_id)
        )
    
    def verify_image_ownership(self, user_id, image_id):
        result = self.select('images', "image_id", where="user_id = %s AND image_id = %s",
                             where_params=(user_id, image_id))
        return bool(result)
    
    def set_user_visited(self, visitor_id, visited_id):
        return self.insert(
            table='visits', 
            data={"visitor_id": visitor_id, "visited_id": visited_id},
            on_conflict="nothing",
            conflict_target=["visitor_id", "visited_id"] 
        )
# def set_user_visited(self, visitor_id, visited_id):
    
    def check_last_visit(self, visitor_id, visited_id):
        result = self.select('visits', "visited_at",
                            where="visitor_id = %s AND visited_id = %s",
                            where_params=(visitor_id, visited_id))
        return result[0]['visited_at'] if result else None

    def get_profile_views(self, user_id):
        result = self.select('visits', "visitor_id", where="visited_id = %s", where_params=(user_id,))
        return [visit['visitor_id'] for visit in result]


    def update_profile_vist_timestamp(self, visitor_id, visited_id):
        return self.insert(
            table='visits', 
            data={"visitor_id": visitor_id, "visited_id": visited_id},
            on_conflict="update",
            conflict_target=["visitor_id", "visited_id"],
            update_set={"visited_at": sql.SQL("CURRENT_TIMESTAMP")}
        )

    def get_fame_rating(self, user_id):
        try:
            result = self.select('profiles', "fame_rating", where="user_id = %s", where_params=(user_id,))
            return result[0]['fame_rating'] if result else 0
        except Exception as e:
            raise Exception(e)
    
    
    def update_fame_rating(self, user_id, new_rating):
        try:
            self.update('profiles', {"fame_rating": new_rating}, where="user_id = %s", where_params=(user_id,))
        except Exception as e:
            raise Exception(e)