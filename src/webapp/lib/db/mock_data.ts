import {hashPassword} from '@/lib/auth/session';
import {User, type NewUser} from '@/lib/db/schema';

let  users:User[] = [
    {
      id: 1,
      name: "Test One",
      email: "testone@test.com",
      passwordHash: "", // Precompute or provide a default hash,
      role: "other",
      stripeCustomerId: "",
      stripeSubscriptionId: "",
      stripeProductId: "",
      planName: "",
      subscriptionStatus: ""
    },
    {
        id: 2,
        name: "Test Two",
        email: "testtwo@test.com",
        passwordHash: "", // Precompute or provide a default hash,
        role: "other",
        stripeCustomerId: "",
        stripeSubscriptionId: "",
        stripeProductId: "",
        planName: "",
        subscriptionStatus: ""
    },
];

(async function generateHashes() {
    for (let i = 0; i < users.length; i++) {
        let password: string = users[i].email;  // same as email
        users[i].passwordHash = await hashPassword(password);
    }
    console.log("Mock Password Hashes Generated")
})();       // Anonymous calling

// Exported Functions Below

export function mock_getUserById(id: number) {
    const idx = users.findIndex(user => user.id === id);
    if (idx !== -1)
        return [users[idx]];
    else
        return []
}

export function mock_getUserByEmail(email: string) {
    const idx = users.findIndex(user => user.email === email);
    if (idx !== -1)
        return [users[idx]];
    else
        return []
}

export function mock_createUser(newuser: NewUser) {
    const id:number = users.length + 1;
    newuser.id = id;
    users.push(newuser as User);
    return [newuser];
}

export function mock_deleteUserById(id: number) {
    const idx = users.findIndex(user => user.id === id);
    if (idx !== -1) 
        users.splice(idx, 1);
}



