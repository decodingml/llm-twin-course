from db.documents import ArticleDocument, PostDocument, RepositoryDocument


def insert_post_into_collection():
    post = {
        "first post": """Excited to share some big news! 🎉 Our team has been working tirelessly on developing a groundbreaking solution designed to revolutionize the tech industry, and today, we're finally ready to unveil it to the world. Introducing InnovateX, our latest product that leverages cutting-edge AI to streamline operations and enhance productivity for businesses globally. 🚀

    InnovateX is not just a product; it's a game-changer. It embodies our commitment to innovation, efficiency, and excellence. By harnessing the power of advanced algorithms and machine learning, InnovateX offers unparalleled insights and automation capabilities that transform the way businesses operate. 🌟

    But what sets InnovateX apart? It's the meticulous attention to detail, the user-centric design, and the relentless pursuit of perfection. Our team has poured their hearts and souls into creating a product that not only meets but exceeds the expectations of our users. From intuitive interfaces to robust security features, InnovateX is built to empower. 💪

    As we embark on this exciting journey, I want to extend my heartfelt thanks to every team member who made this possible. Your dedication, creativity, and passion are what drive our success. To our clients and partners, thank you for believing in us and joining us on this path to innovation. We're thrilled to see how InnovateX will help you achieve your goals and redefine what's possible. 🌈

    Looking ahead, we're committed to continuous improvement and innovation. We believe that the best is yet to come, and with InnovateX, we're just getting started. Stay tuned for more updates, and here's to a future filled with endless possibilities! 🌍

    #Innovation #TechRevolution #InnovateX #TeamSuccess #ThankYou"""
    }
    PostDocument(platform="linkedin", content=post, author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f").save()


def insert_article_into_collection():
    content = {"test": "Test data for a article content"}
    ArticleDocument(
        platform="medium", link="/htttps/alex/paul", content=content, author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f"
    ).save()


def insert_repo_into_collection():
    content = {"test": "Test data for a repo content into db"}
    RepositoryDocument(
        name="test_repo", link="/bla/bla/bla", content=content, owner_id="dbe92510-c33f-4ff7-9908-ee6356fe251f"
    ).save()


if __name__ == "__main__":
    insert_post_into_collection()
