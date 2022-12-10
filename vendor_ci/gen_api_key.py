import secrets
import string

print(
    "tvm_"
    + "".join(
        [secrets.choice(string.digits + string.ascii_lowercase) for _ in range(30)]
    )
)
