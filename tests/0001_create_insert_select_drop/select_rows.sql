select * from clusterAllReplicas(default, db, tbl) order by p;
select hostname(), count() from clusterAllReplicas(default, db, tbl) group by hostname();
