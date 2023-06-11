import axios from "axios";
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import url from "url";

const createOptions = (req) => ({
  secret: process.env.SECRET,
  providers: [
    //GoogleProvider({
     //clientId: process.env.GOOGLE_ID,
     // clientSecret: process.env.GOOGLE_SECRET,
   // }),
    CredentialsProvider({
      // The name to display on the sign in form (e.g. "Sign in with...")
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" ,placeholder:"Input your username" },
        password: { label: "Password", type: "password",placeholder:"Input your password"  },
      },
      async authorize(credentials, req) {
        console.log("credentials", credentials);
        // Add logic here to look up the user from the credentials supplied
        let user = { id: 1, name: "J Smith", email: credentials.username, password: credentials.password };
        if (user) {
          // Any object returned will be saved in `user` property of the JWT
          return user;
        } else {
          // If you return null then an error will be displayed advising the user to check their details.
          return null;

          // You can also Reject this callback with an Error thus the user will be sent to the error page with the error message as a query parameter
        }
      },
    }),
  ],

  pages: {
    //signIn: "/api/auth/signin",
    //signOut: "/api/auth/signout",
    //error: "/api/account/Failure", // Error code passed in query string as ?error=
  },
  theme: {
    colorScheme: "auto", // "auto" | "dark" | "light"
    brandColor: "", // Hex color code
    logo: "/logo.png", // Absolute URL to image
    buttonText: "#2a9f00" // Hex color code
  }
,
  // Callbacks are asynchronous functions you can use to control what happens
  // when an action is performed.
  // https://next-auth.js.org/configuration/callbacks
  callbacks: {
    async signIn({ user, account, profile, email, credentials }) {
      const data = await axios
        .post(process.env.APP_API_END_POINT + "/dt/accounts/auth_user/", { username: user.email, password: user.password })
        .then((result) => {
          if (result.data.code == 0) {
            return false;
          }
          user["data"] = result.data.data;
          return true;
        })
        .catch((error) => {
          console.error("=============AUTH CATCH ERROR========>", error);
          return false;
        });
   
      return data;
    },
    async redirect(url, baseUrl) {
      return "/customer/payment_reminders/";
    },
    async session({ session, token, user }) {
      session.user = token.user;
      return session;
    },
    async jwt({ token, user, account, profile, isNewUser }) {
      const sessionUpdateQuery = url.parse(req.url, true).query.update;
      if (sessionUpdateQuery !== undefined) {
        token.user.data = JSON.parse(sessionUpdateQuery);
      } else {
        user && (token.user = user);
      }
      return token;
    },
  },

  // Events are useful for logging
  // https://next-auth.js.org/configuration/events
  events: {},
  debug: false,
});

export default async (req, res) => {
  return NextAuth(req, res, createOptions(req));
};
