import math

class ReapprovisionnementFixe:
    def __init__(self, delai_livraison, consommation_annuelle, prix_achat_unitaire, taux_possession, cout_lancement):
        self.delai_livraison = delai_livraison
        self.consommation_annuelle = consommation_annuelle
        self.prix_achat_unitaire = prix_achat_unitaire
        self.taux_possession = taux_possession
        self.cout_lancement = cout_lancement

    def calculer_qec(self):
        qec = math.sqrt((2 * self.consommation_annuelle * self.cout_lancement) / (self.prix_achat_unitaire * self.taux_possession))
        return qec

    def calculer_periode_reapprovisionnement(self):
        qec = self.calculer_qec()
        periode = (qec / self.consommation_annuelle) * 365
        return periode

    def calculer_cout_lancement(self):
        qec = self.calculer_qec()
        cout_lancement = (self.consommation_annuelle / qec) * self.cout_lancement
        return cout_lancement

    def calculer_cout_possession(self):
        qec = self.calculer_qec()
        cout_possession = (qec / 2) * self.prix_achat_unitaire * self.taux_possession
        return cout_possession

    def calculer_cout_total_stock(self):
        cout_lancement = self.calculer_cout_lancement()
        cout_possession = self.calculer_cout_possession()
        cout_total = cout_lancement + cout_possession
        return cout_total

class ReapprovisionnementPointCommande:
    def __init__(self, stock_actuel, delai_livraison, taille_lot, consommation_annuelle, prix_achat_unitaire, taux_possession, cout_lancement, stock_securite):
        self.stock_actuel = stock_actuel
        self.delai_livraison = delai_livraison
        self.taille_lot = taille_lot
        self.consommation_annuelle = consommation_annuelle
        self.prix_achat_unitaire = prix_achat_unitaire
        self.taux_possession = taux_possession
        self.cout_lancement = cout_lancement
        self.stock_securite = stock_securite

    def ajuster_quantite_lot(self, quantite):
        return ((quantite + self.taille_lot - 1) // self.taille_lot) * self.taille_lot

    def calculer_qec(self):
        qec = math.sqrt((2 * self.consommation_annuelle * self.cout_lancement) / (self.prix_achat_unitaire * self.taux_possession))
        return qec

    def calculer_point_commande(self):
        consommation_moyenne_jour = self.consommation_annuelle / 365
        point_commande = (consommation_moyenne_jour * self.delai_livraison) + self.stock_securite
        point_commande_ajuste = self.ajuster_quantite_lot(point_commande)
        return point_commande_ajuste

    def calculer_cout_lancement(self):
        qec = self.calculer_qec()
        cout_lancement = (self.consommation_annuelle / qec) * self.cout_lancement
        return cout_lancement

    def calculer_cout_possession(self):
        qec = self.calculer_qec()
        cout_possession = (qec / 2) * self.prix_achat_unitaire * self.taux_possession
        return cout_possession

    def calculer_cout_total_stock(self):
        cout_lancement = self.calculer_cout_lancement()
        cout_possession = self.calculer_cout_possession()
        cout_total = cout_lancement + cout_possession
        return cout_total

    def verifier_et_reapprovisionner(self):
        point_commande = self.calculer_point_commande()
        if self.stock_actuel <= point_commande:
            qec = self.calculer_qec()
            quantite_ajustee = self.ajuster_quantite_lot(qec)
            print(f"Stock actuel ({self.stock_actuel}) inférieur ou égal au point de commande ({point_commande:.2f}). Commande de {quantite_ajustee} unités déclenchée.")
        else:
            print(f"Stock actuel ({self.stock_actuel}) supérieur au point de commande ({point_commande:.2f}). Pas de commande nécessaire.")