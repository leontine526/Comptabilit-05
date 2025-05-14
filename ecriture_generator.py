
from datetime import datetime
from collections import defaultdict

class ComptableIA:
    def __init__(self):
        self.plan_comptable = {
            "achat_marchandises": {"debit": [601, 4456], "credit": 401},
            "vente_marchandises": {"debit": 411, "credit": [701, 4457]},
            "transport": {"debit": 624, "credit": 401},
            "remise": {"debit": 765, "credit": 401},
            "amortissement": {"debit": 681, "credit": 281},
            "immobilisation": {"debit": 215, "credit": 401},
            "salaires": {"debit": 641, "credit": 421},
        }

    def analyser_operation(self, texte):
        texte = texte.lower()
        if "achat" in texte and "marchandises" in texte:
            return "achat_marchandises"
        elif "vente" in texte:
            return "vente_marchandises"
        elif "transport" in texte:
            return "transport"
        elif "remise" in texte or "ristourne" in texte:
            return "remise"
        elif "amortissement" in texte:
            return "amortissement"
        elif "immobilisation" in texte or "matériel" in texte:
            return "immobilisation"
        elif "salaire" in texte:
            return "salaires"
        else:
            return None

    def detecter_mode_paiement(self, texte):
        texte = texte.lower()
        if "comptant" in texte or "espèces" in texte or "cash" in texte:
            return "comptant"
        elif "crédit" in texte:
            return "crédit"
        elif "terme" in texte:
            return "à terme"
        else:
            return "crédit"

    def calculer_tva(self, montant_ht, taux_tva):
        return round(montant_ht * (taux_tva / 100), 2)

    def generer_libelle(self, type_op, montant):
        libelles = {
            "achat_marchandises": f"Achat de marchandises pour {montant} FC",
            "vente_marchandises": f"Vente de marchandises pour {montant} FC", 
            "transport": f"Frais de transport facturés pour {montant} FC",
            "remise": f"Remise commerciale accordée pour {montant} FC",
            "amortissement": f"Dotation aux amortissements pour {montant} FC",
            "immobilisation": f"Acquisition d'immobilisation pour {montant} FC",
            "salaires": f"Paiement des salaires pour {montant} FC"
        }
        return libelles.get(type_op, "Opération comptable")

    def generer_ecriture(self, texte, montant_ht, taux_tva=0, frais_accessoires=0, remise=0, date_op=None, libelle_personnalise=None):
        type_op = self.analyser_operation(texte)
        mode_paiement = self.detecter_mode_paiement(texte)
        if not type_op:
            return {"erreur": "Type d'opération non reconnu"}

        comptes = self.plan_comptable.get(type_op, {})
        tva = self.calculer_tva(montant_ht, taux_tva)
        total = montant_ht + tva + frais_accessoires - remise

        if date_op is None:
            date_op = datetime.today().strftime('%Y-%m-%d')

        if libelle_personnalise is None:
            libelle_personnalise = self.generer_libelle(type_op, montant_ht)

        compte_paiement = 401 if mode_paiement in ["crédit", "à terme"] else 512

        ecriture = {
            "date": date_op,
            "libelle": libelle_personnalise,
            "mode_paiement": mode_paiement,
            "débit": [],
            "crédit": []
        }

        if type_op == "achat_marchandises":
            ecriture["débit"].append({"compte": 601, "montant": montant_ht})
            if taux_tva > 0:
                ecriture["débit"].append({"compte": 4456, "montant": tva})
            if frais_accessoires > 0:
                ecriture["débit"].append({"compte": 624, "montant": frais_accessoires})
            ecriture["crédit"].append({"compte": compte_paiement, "montant": total})

        elif type_op == "vente_marchandises":
            ecriture["débit"].append({"compte": 411, "montant": total})
            ecriture["crédit"].append({"compte": 701, "montant": montant_ht})
            if taux_tva > 0:
                ecriture["crédit"].append({"compte": 4457, "montant": tva})

        elif type_op == "transport":
            ecriture["débit"].append({"compte": 624, "montant": montant_ht})
            ecriture["crédit"].append({"compte": compte_paiement, "montant": montant_ht})

        elif type_op == "remise":
            ecriture["débit"].append({"compte": 765, "montant": remise})
            ecriture["crédit"].append({"compte": compte_paiement, "montant": remise})

        elif type_op == "amortissement":
            ecriture["débit"].append({"compte": 681, "montant": montant_ht})
            ecriture["crédit"].append({"compte": 281, "montant": montant_ht})

        elif type_op == "immobilisation":
            ecriture["débit"].append({"compte": 215, "montant": montant_ht})
            ecriture["crédit"].append({"compte": compte_paiement, "montant": montant_ht})

        elif type_op == "salaires":
            ecriture["débit"].append({"compte": 641, "montant": montant_ht})
            ecriture["crédit"].append({"compte": 421, "montant": montant_ht})

        return ecriture

    def generer_grand_livre(self, ecritures):
        comptes = defaultdict(lambda: {"debit": 0, "credit": 0, "mouvements": []})
        for ecriture in ecritures:
            for ligne in ecriture["débit"]:
                compte = ligne["compte"]
                comptes[compte]["debit"] += ligne["montant"]
                comptes[compte]["mouvements"].append({
                    "type": "débit",
                    "montant": ligne["montant"],
                    "libelle": ecriture["libelle"],
                    "date": ecriture["date"]
                })
            for ligne in ecriture["crédit"]:
                compte = ligne["compte"] 
                comptes[compte]["credit"] += ligne["montant"]
                comptes[compte]["mouvements"].append({
                    "type": "crédit",
                    "montant": ligne["montant"],
                    "libelle": ecriture["libelle"],
                    "date": ecriture["date"]
                })
        return comptes

    def generer_bilan(self, grand_livre):
        actif = {}
        passif = {}
        for compte, valeurs in grand_livre.items():
            solde = valeurs["debit"] - valeurs["credit"]
            if compte < 400:  
                actif[compte] = solde
            else:
                passif[compte] = -solde
        total_actif = sum(actif.values())
        total_passif = sum(passif.values())
        return {
            "actif": actif,
            "passif": passif,
            "total_actif": total_actif,
            "total_passif": total_passif
        }

    def generer_journal_complet(self, operations):
        journal = {
            "libelle_journal": "Journal comptable de l'année",
            "écritures": [],
            "total_débit": 0,
            "total_crédit": 0
        }

        for op in operations:
            ecriture = self.generer_ecriture(
                texte=op.get("texte", ""),
                montant_ht=op.get("montant_ht", 0),
                taux_tva=op.get("taux_tva", 0),
                frais_accessoires=op.get("frais_accessoires", 0),
                remise=op.get("remise", 0),
                date_op=op.get("date_op", None),
                libelle_personnalise=op.get("libelle_personnalise", None)
            )
            journal["écritures"].append(ecriture)
            journal["total_débit"] += sum([e["montant"] for e in ecriture["débit"]])
            journal["total_crédit"] += sum([e["montant"] for e in ecriture["crédit"]])

        grand_livre = self.generer_grand_livre(journal["écritures"])
        bilan = self.generer_bilan(grand_livre)

        return {
            "journal": journal,
            "grand_livre": grand_livre,
            "bilan": bilan
        }
