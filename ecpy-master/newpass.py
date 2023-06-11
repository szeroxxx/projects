from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print(pwd_context.hash('yourpass'))

#print(pwd_context.verify('secret', '$2b$12$mQZnhsrhMvd6hj0U99xuEuftxBoGdET9w7vxTLYNSCF70RDewJznK'))