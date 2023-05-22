import openai

from config.constants import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def generate_talent_prompt(talent):
    return f"""Nestled between the jungle and the beach, Envision Festival is an awakening of the soul. Through an emphasized focus on our pillars of movement, spirituality, music, art, health, sustainability and education, it is so much more than just a music festival.
Envision's mission is to create an eye-opening experience that turns us onto a new form of living; a new way to be inspired. To provide tools that can be integrated into the life we are already living or to inspire a complete shift in our life path. The connection to nature can be felt in every aspect of Envision and the ripple effect of what people then take away from the festival is much more potent than just a good party.

Suggest a bio for a talent that will be present at the festival.

Name: Savej
Main category: Music
Pillars: Music
Country: United States
Message: -
Bio: Born and raised in the Honey Island Swamp of Louisiana, Savej, [pron. savage] is, above all, a student of the wisdom held by ancient cultures. Combining world instruments, the sounds of nature, and shamanic ceremonial influences with hip-hop influenced tribal rhythms and an 808 feel, his music weaves together modern and ancient cultures into one universal, organic, Ancient Future sound.

Name: LUCHO
Main category: Art
Pillars: Art, Spirituality
Country: Costa Rica
Message: I feel very grateful to be part of this great family again, I can't wait to share my art with all of you!
Bio: Luis Castro Barrantes, also known as Lucho is a Costa Rican artist, art director and video producer, in 2020 he entered the NFTS where he became one of the top 10 best-selling artists on the NFT platform Kwnonorigin.io during 2021 His art comes from a mixture of non-conformity and self-reflection, mixing urban culture and graffiti lines with the figurative tradition of Latin American cultures, becoming a representative of an art that is far from the trends of the region. Currently his works, both physical and digital, are found all over the world

Name: Bredevi
Main category: Kids Zone
Pillars: Art, Movement, Spirituality
Country: USA
Message: I’m so excited to be sharing this medicine with people of all ages and backgrounds on the land that has inspired me the most!
Bio: I am a mother of two girls who is deeply passionate about sharing feminine healing with all who are open to receive. In my workshops we approach a variety of creative modalities that guide us back home to the unconditional love of the mother. My intention is to help others experience more safety and bliss in their bodies rather than from external sources.

Name: {talent.get('name')}
Main category: {talent.get('main_category', '-')}
Pillars: {', '.join(talent.get('pillars', []))}
Country: {talent.get('country', '-')}
Message: {talent.get('message', '-')}
Bio: """


def generate_talent_bio(talent: dict):
    prompt = generate_talent_prompt(talent)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.6,
        max_tokens=200
    )
    return response['choices'][0]['text'].strip()
