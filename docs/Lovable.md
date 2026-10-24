> ## Documentation Index
> Fetch the complete documentation index at: https://docs.lovable.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Control who can access your app's data

> Review the row level security policies that decide which rows each user can see or change, ask Lovable to change one, and rotate your database password.

Two things control access to your app's data: the policies that decide which rows each signed-in user can see, and the database password that direct connections use. Lovable sets both up when it builds your app. You can review the policies and rotate the password at any time.

## Row level security (RLS) policies

Row level security (RLS) controls which data users can access across your database, storage, and realtime features, the live updates your app pushes to users. A policy is a rule that decides which rows a signed-in user can see or change, for example "users can only read their own orders".

Lovable sets up these rules automatically when it builds features that store user data, so that one user's private data is not served to another.

To review the rules, go to **More → Database**, select **Manage**, then **Policies**. The policies view lists each policy with:

* **Policy name**: what the rule is for.
* **Command**: the action the rule applies to. SELECT is reading data, INSERT is adding it, UPDATE is changing it, and DELETE is removing it.
* **Applies to**: which users the rule covers, such as signed-in (authenticated) or anonymous (anon) users.
* **Rule expression**: whether the rule has a condition. Expand the row to read the SQL condition that must be true for the action to be allowed.

You can filter by section (**All policies**, **Tables**, **Storage**, or **Realtime**) and by table.

The policies view is read-only. To change a policy, ask Lovable in the project chat, for example:

```text wrap theme={null}
Only allow users to see their own invoices.
```

## Rotate the database password

Your project's database has a password that Lovable manages for you, so you do not need to see or store it. You can ask Lovable to rotate it at any time as a routine security measure. For example, prompt Lovable:

```text wrap theme={null}
Rotate my database password.
```

Lovable generates the new password and asks you to confirm before applying it. Lovable does not show the new password, and your app continues to work without changes. Any tool a developer connected with the old password, such as a business intelligence (BI) tool or a script, stops working until they update it.

Anyone who can manage the project's settings can rotate the password. Lovable rotates the password only for the built-in backend, not for a connected [Supabase](https://docs.lovable.dev/integrations/supabase.md) project. On Enterprise plans, every rotation is recorded in your workspace [audit log](https://docs.lovable.dev/features/audit-logs.md).


## Related topics

- [Control project access](https://docs.lovable.dev/features/project-visibility.md)
- [App + chat connectors: Add capabilities to your published app and your chat](https://docs.lovable.dev/integrations/app-connectors.md)
- [Publish your Lovable project](https://docs.lovable.dev/features/publish.md)
- [Remix a project](https://docs.lovable.dev/features/projects/remix.md)
- [How Lovable hosts your app](https://docs.lovable.dev/features/hosting.md)
