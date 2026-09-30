# Social-media scope clarification (stripe/ft3 issue #2)

The four existing concepts and codes remain; no record is deleted or merged. Broad descriptions previously mixed resource procurement, takeover, lures, identity concealment, and consequences. This proposal distinguishes the existing behavior in each record rather than creating a new identity.

| Record | Defines | Excludes as defining behavior |
| --- | --- | --- |
| FT007.010 | Obtain/create/cultivate accounts as resources, including purchased access | Direct takeover by the buyer (FT008.003) |
| FT008.003 | Unauthorized takeover of an existing social account | Buying access already obtained by someone else (FT007.010) |
| FT018 | Access-seeking social lures, with information capture and malicious-content paths | Account procurement, false identity alone, and later harm |
| FT021 | Present a false trusted identity through a fake or compromised social account | Generic harmful content lacking impersonation |

A sequence may legitimately match several records. FT018 retains Initial Access. FT007.010 and FT008.003 retain Resource Development. FT021 retains Defense Evasion & Obfuscation because the distinguishing act conceals the real operator behind a trusted identity; this is consistent with the current V1 tactic's identity-hiding scope. This is a V1 placement proposal, not an assertion that every impersonation framework assigns that tactic.

Sources: [establish social accounts](https://attack.mitre.org/techniques/T1585/001/), [compromise social accounts](https://attack.mitre.org/techniques/T1586/001/), [phishing via service](https://attack.mitre.org/techniques/T1566/003/), [impersonation](https://attack.mitre.org/techniques/T1656/).

The companion clause-disposition CSV inventories original description/detection sentences. Reassignment means that the edited records explicitly identify the responsible neighbor; it does not claim that every source clause was copied verbatim there. Generic prevention and opaque prediction claims are replaced by evidence/visibility-qualified guidance. Broad harm claims remain possible consequences rather than definitions; standalone harassment or defamatory content is outside these four acquisition/access/identity concepts and is not silently relabeled as impersonation.
