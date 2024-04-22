from db.documents import ArticleDocument, PostDocument, RepositoryDocument


def insert_post_into_collection_1():
    post = {
        "first post": """Excited to share some big news! 🎉 Our team has been working tirelessly on developing a groundbreaking solution designed to revolutionize the tech industry, and today, we're finally ready to unveil it to the world. Introducing InnovateX, our latest product that leverages cutting-edge AI to streamline operations and enhance productivity for businesses globally. 🚀

    InnovateX is not just a product; it's a game-changer. It embodies our commitment to innovation, efficiency, and excellence. By harnessing the power of advanced algorithms and machine learning, InnovateX offers unparalleled insights and automation capabilities that transform the way businesses operate. 🌟

    But what sets InnovateX apart? It's the meticulous attention to detail, the user-centric design, and the relentless pursuit of perfection. Our team has poured their hearts and souls into creating a product that not only meets but exceeds the expectations of our users. From intuitive interfaces to robust security features, InnovateX is built to empower. 💪

    As we embark on this exciting journey, I want to extend my heartfelt thanks to every team member who made this possible. Your dedication, creativity, and passion are what drive our success. To our clients and partners, thank you for believing in us and joining us on this path to innovation. We're thrilled to see how InnovateX will help you achieve your goals and redefine what's possible. 🌈

    Looking ahead, we're committed to continuous improvement and innovation. We believe that the best is yet to come, and with InnovateX, we're just getting started. Stay tuned for more updates, and here's to a future filled with endless possibilities! 🌍

    #Innovation #TechRevolution #InnovateX #TeamSuccess #ThankYou"""
    }
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()

    print("Post inserted into collection")


def insert_post_into_collection_2():
    post = {
        'first post': """Join me in acknowledging the transformative impact of OpenAI's groundbreaking work! From revolutionizing natural language processing to advancing robotics and healthcare, OpenAI's research has far-reaching implications across diverse fields. By fostering collaboration and knowledge sharing, OpenAI is accelerating the pace of innovation and driving progress in AI-driven technologies. As we witness the remarkable achievements of OpenAI, let's continue to support and amplify their efforts in shaping a future where AI serves as a powerful force for innovation and societal benefit. #OpenAI #AI #Innovation #Technology"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_3():
    post = {
        'first post': """Excited to delve deeper into the fascinating realm of Retrieval Augmented Generation (RAG)! This cutting-edge approach combines the strengths of retrieval-based models with generative models, promising groundbreaking advancements in natural language processing (NLP). By enabling systems to retrieve and generate information dynamically, RAG holds immense potential for revolutionizing various applications, from question answering systems to content creation tools. I'm eager to explore how RAG can enhance user experiences, streamline information retrieval processes, and drive innovation across industries. Join me on this journey as we uncover the transformative capabilities of RAG in shaping the future of AI-driven technologies. #RAG #AI #NLP #Innovation"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_4():
    post = {
        'first post': """Just wrapped up an intensive exploration of Retrieval Augmented Generation (RAG), and I'm truly astounded by its potential to redefine the landscape of artificial intelligence! By seamlessly integrating retrieval and generation models, RAG introduces a novel paradigm that empowers AI systems to dynamically retrieve and generate information in real-time. This innovative approach opens up new avenues for enhancing human-computer interactions, enabling more intuitive and contextually relevant responses. From personalized virtual assistants to AI-driven content creation platforms, the applications of RAG are boundless. I'm excited to witness the transformative impact of RAG across various domains and industries. #ArtificialIntelligence #RAG #Innovation #FutureTech"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_5():
    post = {
        'first post': """Are you intrigued by the convergence of retrieval and generation models in natural language processing? Join me on a journey of discovery as we explore the fascinating world of Retrieval Augmented Generation (RAG). By seamlessly integrating the strengths of both approaches, RAG offers a powerful framework for enhancing information retrieval, question answering, and content generation tasks. Its ability to dynamically retrieve and generate contextually relevant responses marks a significant leap forward in AI capabilities. Let's embark on this exploration together and unlock the full potential of RAG in shaping the future of AI-driven technologies. #RAG #AI #NLP #Technology"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe4200-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_6():
    post = {
        'first post': """Just completed an in-depth study of Retrieval Augmented Generation (RAG), and I'm incredibly excited about its transformative potential in natural language processing (NLP). By leveraging the complementary strengths of retrieval-based and generative models, RAG enables AI systems to dynamically retrieve and generate information, leading to more contextually relevant and coherent responses. Whether it's enhancing search engines, improving chatbots, or revolutionizing content creation tools, RAG offers a versatile framework with countless applications. I can't wait to see how this innovative approach will reshape the way we interact with information and AI systems in the years to come. #RAG #NLP #AI #Innovation"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_7():
    post = {
        'first post': """Just completed an in-depth study of Retrieval Augmented Generation (RAG), and I'm incredibly excited about its transformative potential in natural language processing (NLP). By leveraging the complementary strengths of retrieval-based and generative models, RAG enables AI systems to dynamically retrieve and generate information, leading to more contextually relevant and coherent responses. Whether it's enhancing search engines, improving chatbots, or revolutionizing content creation tools, RAG offers a versatile framework with countless applications. I can't wait to see how this innovative approach will reshape the way we interact with information and AI systems in the years to come. #RAG #NLP #AI #Innovation"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_8():
    post = {
        'first post': """Just attended an enlightening webinar on Retrieval Augmented Generation (RAG) and its potential to revolutionize content creation in the digital age. By seamlessly integrating retrieval-based and generative models, RAG offers a unique solution to the challenges of generating high-quality and contextually relevant content. Its ability to dynamically retrieve information from large knowledge bases while generating coherent and engaging narratives opens up exciting possibilities for marketers, writers, and content creators. Whether it's crafting personalized product descriptions or generating compelling blog posts, RAG promises to elevate the art of content creation to new heights. #RAG #ContentCreation #AI #Innovation"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_9():
    post = {
        'first post': """Python classes are a fundamental concept in object-oriented programming, and mastering them is essential for building robust and scalable applications. Whether you're a beginner eager to learn the basics or an experienced developer looking to deepen your understanding, delving into Python classes is a rewarding journey. From encapsulation and inheritance to polymorphism and abstraction, classes empower you to organize your code effectively and create reusable components. Join me in exploring the intricacies of Python classes as we unlock the full potential of object-oriented programming in Python. Let's level up our coding skills together! #Python #Programming #Classes #OOP"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_post_into_collection_10():
    post = {
        'first post': """Let's dive into the world of Python classes! As the building blocks of object-oriented programming in Python, classes play a pivotal role in structuring and organizing code for scalability and maintainability. Whether you're developing web applications, data analysis tools, or machine learning models, understanding how to leverage classes effectively is essential. From defining attributes and methods to implementing inheritance and polymorphism, mastering Python classes empowers you to create elegant and efficient solutions to complex problems. Join me in exploring the depths of Python classes as we elevate our coding skills to new heights! #Python #OOP #Coding #Programming"""}
    PostDocument(
        platform="linkedin",
        content=post,
        author_id="dbe4200-c33f-4ff7-9908-ee6356fe251f",
    ).save()
    print("Post inserted into collection")


def insert_article_into_collection_1():
    content = {"test": "Test data for a article content"}
    ArticleDocument(
        platform="medium",
        link="/htttps/alex/paul",
        content=content,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()

    print("Article inserted into collection")


def insert_article_into_collection_2():
    content = {"test": """Retrieval Augmented Generation (RAG) represents a cutting-edge approach in the field of natural language processing (NLP) that merges the strengths of retrieval-based models and generative models. The key concept behind RAG is its ability to dynamically retrieve relevant information from a large corpus or knowledge base and seamlessly incorporate it into generative responses.
    In traditional generative models, outputs are generated based solely on the internal knowledge of the model. This can lead to issues with outdated information or hallucinations, where the model creates content that seems plausible but is factually incorrect. RAG mitigates these risks by integrating retrieval components that can access up-to-date and contextually appropriate information in real-time. This hybrid approach enhances accuracy and contextual relevance, making it ideal for applications like question answering, chatbots, and content creation tools.
    RAG's impact is transformative, enabling AI systems to provide more reliable and accurate responses while adapting to changing information landscapes. This flexibility opens the door to a range of new possibilities, from personalized virtual assistants to intelligent document summarization. As RAG continues to evolve, it holds great promise for revolutionizing how we interact with AI systems and extract valuable insights from large volumes of data."""}
    ArticleDocument(
        platform="medium",
        link="/htttps/alex/paul",
        content=content,
        author_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()

    print("Article inserted into collection")


def insert_repo_into_collection():
    content = {"test": "Test data for a repo content into db"}
    RepositoryDocument(
        name="test_repo",
        link="/bla/bla/bla",
        content=content,
        owner_id="dbe92510-c33f-4ff7-9908-ee6356fe251f",
    ).save()

    print("Repository inserted into collection")


if __name__ == "__main__":
    insert_post_into_collection_1()
    insert_post_into_collection_2()
    insert_post_into_collection_3()
    insert_post_into_collection_4()
    insert_post_into_collection_5()
    insert_post_into_collection_6()
    insert_post_into_collection_7()
    insert_post_into_collection_8()
    insert_post_into_collection_9()
    insert_post_into_collection_10()
    insert_article_into_collection_1()
    insert_article_into_collection_2()
    insert_repo_into_collection()
