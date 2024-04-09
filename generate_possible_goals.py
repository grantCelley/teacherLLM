import ollama

MODEL = "dolphin-mistral:7b-v2.8-q2_K"

def generate_topics(course_name: str, summary: str):

    system_prompt = f"You are a Phd Educator. I will give you a wikipedia summary generate an outline for a course about the material."
    user_prompt = "{{good article}}\n{{Short description|Branch of mathematics}}\n{{About||the kind of algebraic structure|Algebra over a field|other uses}}\n{{Pp-move}}\n{{Pp-semi-indef}}\n{{multiple image\n|perrow=1 / 1\n|total_width=350\n|image1=Polynomial2.svg\n|alt1=Polynomial equation\n|link1=Polynomial equation\n|image2=Ring of integers2.svg\n|alt2=Signature of the ring of integers\n|link2=Ring of integers\n|footer=[[Elementary algebra]] is interested in [[polynomial equations]] and seeks to discover which values [[Equation solving|solve them]] (top image). [[Abstract algebra]] studies [[algebraic structure]]s, like the [[ring of integers]] given by the set of [[integer]]s (<math>\\Z</math>) together with [[Algebraic operation|operations]] of [[addition]] (<math>+</math>) and [[multiplication]] (<math>\\times</math>) (bottom image).\n}}\n\n'''Algebra''' is the branch of [[mathematics]] that studies [[algebraic structures]] and the manipulation of statements within those structures. It is a generalization of [[arithmetic]] that introduces [[Variable (mathematics)|variables]] and [[algebraic operation]]s other than the standard arithmetic operations such as [[addition]] and [[multiplication]].\n\n[[Elementary algebra]] is the main form of algebra taught in school and examines mathematical statements using variables for unspecified values. It seeks to determine for which values the statements are true. To do so, it utilizes different methods of transforming equations to isolate variables. [[Linear algebra]] is a closely related field investigating variables that appear in several [[linear equation]]s, so-called [[systems of linear equations]]. It tries to discover the values that solve all equations at the same time.\n\n[[Abstract algebra]] studies algebraic structures, which consist of a [[Set (mathematics)|set]] of [[mathematical objects]] together with one or several [[binary operations]] defined on that set. It is a generalization of elementary and linear algebra since it allows mathematical objects other than numbers and non-arithmetic operations. It distinguishes between different types of algebraic structures, such as [[Group (mathematics)|groups]], [[Ring (mathematics)|rings]], and [[Field (mathematics)|fields]], based on the number of operations they use and the [[Axiom|laws they follow]]. [[Universal algebra]] constitutes a further level of generalization that is not limited to binary operations and investigates more abstract patterns that characterize different classes of algebraic structures.\n\nAlgebraic methods were first studied in the [[ancient period]] to solve specific problems in fields like [[geometry]]. Subsequent mathematicians examined general techniques to solve equations independent of their specific applications. They relied on verbal descriptions of problems and solutions until the 16th and 17th centuries, when a rigorous mathematical formalism was developed. In the mid-19th century, the scope of algebra broadened beyond a [[theory of equations]] to cover diverse types of algebraic operations and algebraic structures. Algebra is relevant to many branches of mathematics, like geometry, [[topology]], [[number theory]], and [[calculus]], and other fields of inquiry, like [[logic]] and the [[empirical sciences]].\n\n"

    response = ollama.chat(MODEL, messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role":"user",
            "content": user_prompt
        }
    ])

    print(response)

generate_topics("","")